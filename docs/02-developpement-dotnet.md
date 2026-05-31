# Phase 2 : Développement .NET 9 (H12 - H24)

---

## 1. Installation du SDK .NET 9

### Pourquoi .NET 9 ?
.NET 9 est la dernière version du framework Microsoft. Elle apporte :
- **Performance** : JIT plus rapide, GC amélioré
- **Minimal API** : Création d'APIs avec très peu de code
- **Razor Pages** : Architecture simple pour sites web dynamiques
- **Cross-platform** : Fonctionne parfaitement sur Linux

### Installation sur Debian 12

```bash
# Ajouter le dépôt Microsoft
wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

# Mettre à jour et installer le SDK
sudo apt update
sudo apt install -y dotnet-sdk-9.0

# Vérifier l'installation
dotnet --version
# Résultat attendu : 9.0.x
```

### Création de la structure des projets

```bash
# Retourner dans le répertoire du challenge
cd /home/akaletekoffilevis/Bureau/Challenge

# Créer le dossier des sites
mkdir -p sites

# Vérification
ls -la
```

---

## 2. Projet Site Vitrine : Razor Pages (www.nextdev.ne)

### Qu'est-ce que Razor Pages ?
Razor Pages est un modèle de programmation d'ASP.NET Core qui simplifie la création de pages web. Chaque page est un fichier `.cshtml` avec son propre modèle (PageModel).

### Création du projet

```bash
cd sites

# Créer le projet Razor Pages
dotnet new razor -n NextDev.Web -o www.nextdev.ne

# Aller dans le dossier du projet
cd www.nextdev.ne
```

### Structure du projet Razor

```
www.nextdev.ne/
├── Program.cs          # Point d'entrée de l'application
├── appsettings.json    # Configuration
├── Pages/
│   ├── Index.cshtml    # Page d'accueil
│   ├── Index.cshtml.cs # Modèle de la page d'accueil
│   ├── Privacy.cshtml  # Page de confidentialité
│   └── _Layout.cshtml  # Layout commun (header, footer)
├── wwwroot/           # Fichiers statiques (CSS, JS)
└── Properties/
    └── launchSettings.json
```

### Configuration du port d'écoute

Modifier `Properties/launchSettings.json` :

```bash
nano Properties/launchSettings.json
```

```json
{
  "profiles": {
    "NextDev.Web": {
      "commandName": "Project",
      "applicationUrl": "http://0.0.0.0:5000",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      }
    }
  }
}
```

### Personnalisation de la page d'accueil

Éditer `Pages/Index.cshtml` :

```bash
nano Pages/Index.cshtml
```

```html
@page
@model IndexModel
@{
    ViewData["Title"] = "Accueil";
}

<div class="text-center">
    <h1 class="display-4">Bienvenue sur NextDev</h1>
    <p class="lead">
        Challenge d'hébergement .NET 9 — 48 heures
    </p>
    <hr class="my-4">
    <div class="row">
        <div class="col-md-4">
            <h3>Infrastructure</h3>
            <p>DNS, DHCP, Apache2 configurés sur Debian 12</p>
        </div>
        <div class="col-md-4">
            <h3>Développement</h3>
            <p>ASP.NET Core 9 : Razor Pages & Minimal API</p>
        </div>
        <div class="col-md-4">
            <h3>Base de données</h3>
            <p>SQLite pour la persistance des données</p>
        </div>
    </div>
    <div class="mt-4">
        <a class="btn btn-primary btn-lg" href="/Privacy">En savoir plus</a>
    </div>
</div>
```

### Personnalisation du Layout

Éditer `Pages/Shared/_Layout.cshtml` :

```bash
nano Pages/Shared/_Layout.cshtml
```

Modifier le header :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>@ViewData["Title"] - NextDev</title>
    <link rel="stylesheet" href="~/lib/bootstrap/dist/css/bootstrap.min.css" />
    <link rel="stylesheet" href="~/css/site.css" />
</head>
<body>
    <header>
        <nav class="navbar navbar-expand-sm navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">NextDev Challenge</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link" href="/">Accueil</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/Privacy">Confidentialité</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    </header>

    <main role="main" class="pb-3">
        @RenderBody()
    </main>

    <footer class="border-top footer text-muted bg-light">
        <div class="container">
            &copy; 2026 - NextDev Challenge - Hébergement .NET 9
        </div>
    </footer>

    <script src="~/lib/jquery/dist/jquery.min.js"></script>
    <script src="~/lib/bootstrap/dist/js/bootstrap.bundle.min.js"></script>
    <script src="~/js/site.js"></script>
    @await RenderSectionAsync("Scripts", required: false)
</body>
</html>
```

### Configuration pour Kestrel (port 5000)

Éditer `Program.cs` :

```bash
nano Program.cs
```

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();

// Configuration explicite du port
builder.WebHost.UseUrls("http://0.0.0.0:5000");

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

app.UseStaticFiles();
app.UseRouting();
app.MapRazorPages();

app.Run();
```

### Test du site vitrine

```bash
# Lancer le projet
dotnet run &

# Tester avec curl
curl http://localhost:5000
# Résultat attendu : page HTML avec "Bienvenue sur NextDev"
```

---

## 3. Projet API : Minimal API (api.nextdev.ne)

### Qu'est-ce que Minimal API ?
Minimal API est une approche d'ASP.NET Core qui permet de créer des APIs REST avec un minimum de code. Fini les contrôleurs verbeux, on écrit directement les endpoints.

### Création du projet

```bash
cd /home/akaletekoffilevis/Bureau/Challenge/sites

# Créer le projet API
dotnet new webapi -n NextDev.Api --use-minimal-apis -o api.nextdev.ne

# Aller dans le dossier
cd api.nextdev.ne
```

### Installation d'Entity Framework Core + SQLite

```bash
dotnet add package Microsoft.EntityFrameworkCore.Sqlite
dotnet add package Microsoft.EntityFrameworkCore.Design
```

### Structure du projet API

```
api.nextdev.ne/
├── Program.cs              # Point d'entrée + endpoints
├── appsettings.json        # Configuration
├── Models/
│   └── Trainee.cs          # Modèle Stagiaire
├── Data/
│   └── AppDbContext.cs     # Contexte BDD
├── Properties/
│   └── launchSettings.json
```

### Création du modèle Trainee

```bash
mkdir -p Models
nano Models/Trainee.cs
```

```csharp
using System.ComponentModel.DataAnnotations;

namespace NextDev.Api.Models;

public class Trainee
{
    public int Id { get; set; }

    [Required(ErrorMessage = "Le nom est requis")]
    [MaxLength(100)]
    public string Nom { get; set; } = string.Empty;

    [Required(ErrorMessage = "Le prénom est requis")]
    [MaxLength(100)]
    public string Prenom { get; set; } = string.Empty;

    [Required(ErrorMessage = "L'email est requis")]
    [EmailAddress(ErrorMessage = "Format email invalide")]
    [MaxLength(200)]
    public string Email { get; set; } = string.Empty;

    [DataType(DataType.Date)]
    public DateTime DateNaissance { get; set; }

    public DateTime DateInscription { get; set; } = DateTime.UtcNow;
}
```

### Création du DbContext

```bash
mkdir -p Data
nano Data/AppDbContext.cs
```

```csharp
using Microsoft.EntityFrameworkCore;
using NextDev.Api.Models;

namespace NextDev.Api.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Trainee> Trainees => Set<Trainee>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<Trainee>(entity =>
        {
            entity.ToTable("Trainees");
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.Email).IsUnique();
        });
    }
}
```

### Configuration de Program.cs avec les endpoints

```bash
nano Program.cs
```

```csharp
using Microsoft.EntityFrameworkCore;
using NextDev.Api.Data;
using NextDev.Api.Models;

var builder = WebApplication.CreateBuilder(args);

// Configuration SQLite
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Data Source=nextdev.db";
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite(connectionString));

// Configuration du port
builder.WebHost.UseUrls("http://0.0.0.0:5001");

// Swagger pour la documentation
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Créer la base de données au démarrage
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
}

// Middleware
app.UseSwagger();
app.UseSwaggerUI();

// ========== ENDPOINTS ==========

// GET / : Page d'accueil de l'API
app.MapGet("/", () =>
{
    return Results.Ok(new
    {
        Message = "Bienvenue sur l'API NextDev",
        Version = "1.0",
        Endpoints = new[]
        {
            new { Method = "GET", Path = "/", Description = "Accueil de l'API" },
            new { Method = "GET", Path = "/trainee", Description = "Liste des stagiaires" }
        }
    });
})
.WithName("Home")
.WithOpenApi();

// GET /trainee : Liste des stagiaires
app.MapGet("/trainee", async (AppDbContext db) =>
{
    var trainees = await db.Trainees
        .OrderBy(t => t.Nom)
        .ThenBy(t => t.Prenom)
        .ToListAsync();

    return Results.Ok(new
    {
        Count = trainees.Count,
        Data = trainees
    });
})
.WithName("GetTrainees")
.WithOpenApi();

app.Run();
```

### Configuration de la chaîne de connexion

```bash
nano appsettings.json
```

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=nextdev.db"
  }
}
```

### Ajout d'un endpoint POST (optionnel mais utile pour le test)

Si vous voulez ajouter des stagiaires via l'API, ajoutez dans `Program.cs` :

```csharp
// POST /trainee : Ajouter un stagiaire
app.MapPost("/trainee", async (Trainee trainee, AppDbContext db) =>
{
    // Validation
    if (string.IsNullOrWhiteSpace(trainee.Nom))
        return Results.BadRequest(new { Error = "Le nom est requis" });

    if (string.IsNullOrWhiteSpace(trainee.Prenom))
        return Results.BadRequest(new { Error = "Le prénom est requis" });

    // Vérifier si l'email existe déjà
    var exists = await db.Trainees.AnyAsync(t => t.Email == trainee.Email);
    if (exists)
        return Results.Conflict(new { Error = "Cet email existe déjà" });

    db.Trainees.Add(trainee);
    await db.SaveChangesAsync();

    return Results.Created($"/trainee/{trainee.Id}", trainee);
})
.WithName("CreateTrainee")
.WithOpenApi();
```

### Test de l'API

```bash
# Lancer l'API
dotnet run &

# Tester l'accueil
curl http://localhost:5001
# Résultat : { "message": "Bienvenue sur l'API NextDev", ... }

# Tester la liste des stagiaires
curl http://localhost:5001/trainee
# Résultat : { "count": 0, "data": [] }

# Ajouter un stagiaire (si POST implémenté)
curl -X POST http://localhost:5001/trainee \
  -H "Content-Type: application/json" \
  -d '{"nom":"Dupont","prenom":"Jean","email":"jean.dupont@email.com","dateNaissance":"2000-01-15"}'

# Vérifier l'ajout
curl http://localhost:5001/trainee
# Résultat : { "count": 1, "data": [{ "id": 1, "nom": "Dupont", ... }] }
```

---

## 4. Peuplement de la base de données

Pour avoir des données de démonstration, nous pouvons créer un seedeur.

```bash
mkdir -p Data
nano Data/DbSeeder.cs
```

```csharp
using Microsoft.EntityFrameworkCore;
using NextDev.Api.Models;

namespace NextDev.Api.Data;

public static class DbSeeder
{
    public static void Seed(AppDbContext db)
    {
        if (db.Trainees.Any()) return;

        var trainees = new List<Trainee>
        {
            new()
            {
                Nom = "Diop",
                Prenom = "Fatou",
                Email = "fatou.diop@email.com",
                DateNaissance = new DateTime(2001, 3, 15),
                DateInscription = DateTime.UtcNow
            },
            new()
            {
                Nom = "Koné",
                Prenom = "Amadou",
                Email = "amadou.kone@email.com",
                DateNaissance = new DateTime(1999, 7, 22),
                DateInscription = DateTime.UtcNow
            },
            new()
            {
                Nom = "Traoré",
                Prenom = "Aminata",
                Email = "aminata.traore@email.com",
                DateNaissance = new DateTime(2002, 11, 8),
                DateInscription = DateTime.UtcNow
            },
            new()
            {
                Nom = "Ndiaye",
                Prenom = "Moussa",
                Email = "moussa.ndiaye@email.com",
                DateNaissance = new DateTime(2000, 5, 30),
                DateInscription = DateTime.UtcNow
            },
            new()
            {
                Nom = "Diallo",
                Prenom = "Mariam",
                Email = "mariam.diallo@email.com",
                DateNaissance = new DateTime(2003, 1, 12),
                DateInscription = DateTime.UtcNow
            }
        };

        db.Trainees.AddRange(trainees);
        db.SaveChanges();
    }
}
```

Appeler le seedeur dans `Program.cs` :

```csharp
// Ajouter après db.Database.EnsureCreated();
DbSeeder.Seed(db);
```

---

## 5. Script de démarrage des services .NET

Pour lancer automatiquement les deux projets, créer un script :

```bash
cd /home/akaletekoffilevis/Bureau/Challenge
nano start-dotnet.sh
```

```bash
#!/bin/bash

echo "=== Démarrage des services .NET 9 ==="

# Site Vitrine (port 5000)
echo "[1/2] Démarrage de NextDev.Web (Razor Pages) sur :5000..."
cd /home/akaletekoffilevis/Bureau/Challenge/sites/www.nextdev.ne
dotnet run --configuration Release &
PID_WEB=$!
echo "  PID: $PID_WEB"

# API (port 5001)
echo "[2/2] Démarrage de NextDev.Api (Minimal API) sur :5001..."
cd /home/akaletekoffilevis/Bureau/Challenge/sites/api.nextdev.ne
dotnet run --configuration Release &
PID_API=$!
echo "  PID: $PID_API"

echo ""
echo "=== Services démarrés ==="
echo "Site vitrine : http://localhost:5000"
echo "API          : http://localhost:5001"
echo "Stagiaires   : http://localhost:5001/trainee"
echo ""

# Attendre l'arrêt
wait
```

Rendre exécutable :

```bash
chmod +x start-dotnet.sh
```

---

## Résumé Phase 2

À la fin de cette phase, nous avons :
- [x] SDK .NET 9 installé
- [x] Site vitrine **Razor Pages** sur le port **5000**
  - Page d'accueil personnalisée
  - Thème Bootstrap
- [x] **Minimal API** sur le port **5001**
  - `GET /` → informations de l'API
  - `GET /trainee` → liste des stagiaires (SQLite)
  - Modèle `Trainee` avec validation
  - Base de données SQLite
- [x] Données de démonstration (5 stagiaires)
- [x] Script `start-dotnet.sh` pour lancer les deux projets
