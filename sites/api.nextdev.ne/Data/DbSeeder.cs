using NextDev.Api.Models;
namespace NextDev.Api.Data;
public static class DbSeeder
{
    public static void Seed(AppDbContext db)
    {
        if (db.Trainees.Any()) return;
        db.Trainees.AddRange(
            new Trainee { Nom = "Diop", Prenom = "Fatou", Email = "fatou.diop@email.com", DateNaissance = new DateTime(2001,3,15) },
            new Trainee { Nom = "Koné", Prenom = "Amadou", Email = "amadou.kone@email.com", DateNaissance = new DateTime(1999,7,22) },
            new Trainee { Nom = "Traoré", Prenom = "Aminata", Email = "aminata.traore@email.com", DateNaissance = new DateTime(2002,11,8) },
            new Trainee { Nom = "Ndiaye", Prenom = "Moussa", Email = "moussa.ndiaye@email.com", DateNaissance = new DateTime(2000,5,30) },
            new Trainee { Nom = "Diallo", Prenom = "Mariam", Email = "mariam.diallo@email.com", DateNaissance = new DateTime(2003,1,12) }
        );
        db.SaveChanges();
    }
}
