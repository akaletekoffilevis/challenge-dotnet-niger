# Challenge NextDev — Hébergement .NET 9
## Présentation pour le Jury

---

## Slide 1 : Page de Titre

```
╔══════════════════════════════════════════════════════════╗
║  ██╗  ██╗███████╗██╗  ██╗██████╗ ███████╗██╗   ██╗     ║
║  ╚██╗██╔╝██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██║   ██║     ║
║   ╚███╔╝ █████╗   ╚███╔╝ ██║  ██║█████╗  ██║   ██║     ║
║   ██╔██╗ ██╔══╝   ██╔██╗ ██║  ██║██╔══╝  ╚██╗ ██╔╝     ║
║  ██╔╝ ██╗███████╗██╔╝ ██╗██████╔╝███████╗ ╚████╔╝      ║
║  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝  ╚═══╝       ║
║                                                          ║
║              Challenge NextDev                           ║
║           Hébergement .NET 9                             ║
║                                                          ║
║   Configuration d'infrastructure Open Source             ║
║   et déploiement applicatif Full-Stack                   ║
║   en 48 heures                                           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## Slide 2 : Contexte & Périmètre du Projet

### Domaines Cibles
- **www.nextdev.ne** — Site Vitrine (Razor Pages)
- **api.nextdev.ne** — Backend API (Minimal API)

### Technologies Clés
- ASP.NET Core 9 (Razor Pages & Minimal API)
- Base de données SQLite (portable, zéro configuration)
- Infrastructure : DNS (BIND9), DHCP (ISC), Apache 2
- OS : Debian 12 (Bookworm)

---

## Slide 3 : Architecture Globale

```
                     ┌──────────────────────────────────────┐
                     │          Debian 12 Server             │
                     │          10.0.0.68                │
                     │                                      │
       ┌─────────┐   │  ┌──────────┐     ┌──────────────┐   │
       │  Client  │───┼─►│  Apache  │────►│ Kestrel :5000 │   │
       │Navigateur│   │  │ Reverse  │     │ Razor Pages   │   │
       └─────────┘   │  │  Proxy   │     └──────────────┘   │
                     │  │ :80/:443 │                        │
       ┌─────────┐   │  │          │     ┌──────────────┐   │
       │  Client  │───┼─►│          │────►│ Kestrel :5001 │   │
       │   API    │   │  └──────────┘     │ Minimal API   │   │
       └─────────┘   │       │            └──────┬───────┘   │
                     │       │                   │           │
                     │  ┌────┴────┐     ┌────────┴────────┐  │
                     │  │ BIND9   │     │    SQLite       │  │
                     │  │ DNS :53 │     │ (nextdev.db)    │  │
                     │  └─────────┘     └─────────────────┘  │
                     │  ┌─────────┐                          │
                     │  │ ISC DHCP│                          │
                     │  │   :67   │                          │
                     │  └─────────┘                          │
                     └──────────────────────────────────────┘
```

---

## Slide 4 : Infrastructure Réseau & Serveur

### DNS (BIND9)
- Zone `nextdev.ne` configurée
- Enregistrements :
  - `www.nextdev.ne` → `10.0.0.68`
  - `api.nextdev.ne` → `10.0.0.68`
  - `ns1.nextdev.ne` → `10.0.0.68`
- Testé avec `dig` et `nslookup`

### DHCP (ISC-DHCP)
- Plage d'adresses : `10.0.0.50` → `10.0.0.200`
- Bail par défaut : 600s, max : 7200s
- Option routeur : `10.0.0.1`
- Serveurs DNS transmis aux clients

### Apache 2
- Modules : `proxy`, `proxy_http`, `rewrite`, `ssl`, `headers`
- 2 VirtualHosts : www et api
- Reverse Proxy vers Kestrel

### Sécurité (UFW)
- Ports ouverts : 22 (SSH), 80 (HTTP), 443 (HTTPS), 53 (DNS), 67 (DHCP)

---

## Slide 5 : Développement .NET 9

### Site Vitrine — Razor Pages (www.nextdev.ne)
| Élément | Détail |
|---|---|
| Framework | ASP.NET Core 9 |
| Port interne | 5000 |
| Pages | Accueil, Confidentialité |
| UI | Bootstrap 5 responsive |
| Layout | Header personnalisé + footer |

**Program.cs :**
```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
builder.WebHost.UseUrls("http://0.0.0.0:5000");
var app = builder.Build();
app.MapRazorPages();
app.Run();
```

### API REST — Minimal API (api.nextdev.ne)
| Élément | Détail |
|---|---|
| Framework | ASP.NET Core 9 Minimal API |
| Port interne | 5001 |
| Endpoints | `GET /`, `GET /trainee`, `POST /trainee` |
| ORM | Entity Framework Core |
| BDD | SQLite |

**Endpoints :**
```csharp
app.MapGet("/", () => Results.Ok(new {
    Message = "Bienvenue sur l'API NextDev",
    Version = "1.0"
}));

app.MapGet("/trainee", async (AppDbContext db) => {
    var trainees = await db.Trainees.ToListAsync();
    return Results.Ok(new { Count = trainees.Count, Data = trainees });
});
```

---

## Slide 6 : Base de Données SQLite

### Modèle Trainee
```csharp
public class Trainee {
    public int Id { get; set; }
    public string Nom { get; set; }
    public string Prenom { get; set; }
    public string Email { get; set; }
    public DateTime DateNaissance { get; set; }
    public DateTime DateInscription { get; set; }
}
```

### Configuration EF Core
- `DbContext` avec `DbSet<Trainee>`
- Table unique : `Trainees`
- Index unique sur `Email`
- `EnsureCreated()` au démarrage
- Migration automatique

### Données de démonstration
| Nom | Prénom | Email |
|---|---|---|
| Diop | Fatou | fatou.diop@email.com |
| Koné | Amadou | amadou.kone@email.com |
| Traoré | Aminata | aminata.traore@email.com |
| Ndiaye | Moussa | moussa.ndiaye@email.com |
| Diallo | Mariam | mariam.diallo@email.com |

---

## Slide 7 : Reverse Proxy Apache

### Principe de fonctionnement
```
Client ──► HTTP ──► Apache (80/443) ──► ProxyPass ──► Kestrel (5000/5001)
                        │
                        ├── www.nextdev.ne ──► http://localhost:5000
                        └── api.nextdev.ne ──► http://localhost:5001
```

### Configuration VirtualHost
```apache
<VirtualHost *:80>
    ServerName www.nextdev.ne
    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/
    RequestHeader set X-Forwarded-Proto "http"
</VirtualHost>
```

### Sécurité SSL/TLS
- Certificats Let's Encrypt via Certbot
- Redirection automatique HTTP → HTTPS
- Renouvellement automatique des certificats

### Optimisations
- Compression Gzip (mod_deflate)
- Cache des fichiers statiques (mod_expires)
- Headers de sécurité (ServerSignature Off)

---

## Slide 8 : Tests & Résultats

### Tests fonctionnels
| Test | Statut |
|---|---|
| Résolution DNS `www.nextdev.ne` | ✅ |
| Résolution DNS `api.nextdev.ne` | ✅ |
| DHCP attribue les IPs | ✅ |
| www.nextdev.ne → Apache → Kestrel :5000 | ✅ |
| api.nextdev.ne → Apache → Kestrel :5001 | ✅ |
| `GET /trainee` retourne JSON | ✅ |
| HTTPS fonctionnel (Let's Encrypt) | ✅ |

### Tests de performance (Apache Bench)
- 100 requêtes, 10 concurrentes
- 0 requête échouée
- Temps de réponse moyen < 50ms

### Tests de résilience
- Redémarrage Apache : services toujours accessibles
- Redémarrage .NET : reprise automatique
- Fonctionnement sans accès Internet

---

## Slide 9 : Difficultés Rencontrées & Solutions

### Défis techniques
| Difficulté | Solution |
|---|---|
| Syntaxe stricte de BIND9 | Utilisation de `named-checkconf` + logs |
| Communication Apache ↔ Kestrel | Forwarded Headers Middleware |
| IP du client perdue par le proxy | Configuration `X-Forwarded-For` |
| Gestion des ports | `netstat` + `UFW` pour le diagnostic |
| Coordination d'équipe sur 48h | Scripts automatisés + réunions régulières |

### Leçons apprises
- Importance de la documentation en temps réel
- Tests continus plutôt qu'à la fin
- Communication d'équipe : clé du succès

---

## Slide 10 : Travail d'Équipe & Communication

### Organisation
- **4 rôles distincts** : Infrastructure, Web, API, Intégration
- **Réunions régulières** : toutes les 4 heures
- **Documentation commune** : partage des connaissances
- **Entraide** : sur les modules critiques (Reverse Proxy)

### Clés du succès
- Partage des connaissances en Networking
- Coordination sur les scripts de déploiement
- Soutien mutuel durant la phase de débogage
- Objectif commun : livrer un projet complet et fonctionnel

---

## Slide 11 : Conclusion & Remerciements

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              Merci pour votre attention !                ║
║                                                          ║
║           NextDev Challenge | 48 Heures | .NET 9         ║
║                                                          ║
║                                                          ║
║        ✅  Projet fonctionnel de bout en bout             ║
║        ✅  Architecture scalable et sécurisée             ║
║        ✅  Stack technique maîtrisée                      ║
║        ✅  Collaboration d'équipe efficace                ║
║                                                          ║
║                                                          ║
║                Des questions ?                            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## Annexe : Endpoints API

| Méthode | URL | Description | Exemple de réponse |
|---|---|---|---|
| GET | `/` | Accueil API | `{ "message": "Bienvenue...", "version": "1.0", "endpoints": [...] }` |
| GET | `/trainee` | Liste stagiaires | `{ "count": 5, "data": [ { "id": 1, "nom": "Diop", ... } ] }` |
| GET | `/swagger` | Documentation Swagger UI | Interface interactive OpenAPI |
| POST | `/trainee` | Ajouter stagiaire | `{ "id": 6, "nom": "Sow", "prenom": "Awa", ... }` |

## Annexe : Commandes de vérification

```bash
# Tester le DNS
dig www.nextdev.ne +short

# Tester le site via Apache
curl -s http://www.nextdev.ne | head -5

# Tester l'API
curl -s http://api.nextdev.ne/trainee | python3 -m json.tool

# Swagger UI
curl -s http://api.nextdev.ne/swagger | head -10

# Vérifier les services
systemctl status apache2 bind9 isc-dhcp-server --no-pager

# Test de charge
ab -n 100 -c 10 http://www.nextdev.ne/
```
