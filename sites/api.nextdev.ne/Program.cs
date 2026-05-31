using Microsoft.EntityFrameworkCore;
using NextDev.Api.Data;
using NextDev.Api.Models;
var builder = WebApplication.CreateBuilder(args);
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") ?? "Data Source=nextdev.db";
builder.Services.AddDbContext<AppDbContext>(options => options.UseSqlite(connectionString));
builder.WebHost.UseUrls("http://0.0.0.0:5001");
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
var app = builder.Build();
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
    DbSeeder.Seed(db);
}
app.UseSwagger();
app.UseSwaggerUI();
app.MapGet("/", () => Results.Ok(new
{
    Message = "Bienvenue sur l'API NextDev",
    Version = "1.0",
    Endpoints = new[] {
        new { Method = "GET", Path = "/", Description = "Accueil" },
        new { Method = "GET", Path = "/trainee", Description = "Liste des stagiaires" }
    }
}));
app.MapGet("/trainee", async (AppDbContext db) =>
{
    var trainees = await db.Trainees.OrderBy(t => t.Nom).ToListAsync();
    return Results.Ok(new { Count = trainees.Count, Data = trainees });
});
app.Run();
