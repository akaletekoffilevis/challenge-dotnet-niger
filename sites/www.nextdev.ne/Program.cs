var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
builder.WebHost.UseUrls("http://0.0.0.0:5000");
var app = builder.Build();
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
}
app.UseStaticFiles();
app.UseRouting();
app.MapRazorPages();
app.Run();
