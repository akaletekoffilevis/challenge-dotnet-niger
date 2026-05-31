using Microsoft.EntityFrameworkCore;
using NextDev.Api.Models;
namespace NextDev.Api.Data;
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
    public DbSet<Trainee> Trainees => Set<Trainee>();
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Trainee>(entity =>
        {
            entity.ToTable("Trainees");
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.Email).IsUnique();
        });
    }
}
