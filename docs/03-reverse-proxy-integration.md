# Phase 3 : Reverse Proxy Apache & Intégration (H24 - H36)

---

## 1. Concept du Reverse Proxy

### Qu'est-ce qu'un Reverse Proxy ?

Un **Reverse Proxy** est un serveur (ici Apache2) qui se place entre les clients et nos applications .NET (Kestrel). 

```
Client (navigateur)
      │
      ▼
┌─────────────────────┐
│   Apache (port 80)  │◄── Reverse Proxy
│   www.nextdev.ne    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Kestrel (port 5000) │◄── Serveur applicatif .NET
│  Razor Pages        │
└─────────────────────┘
```

### Pourquoi utiliser un Reverse Proxy ?

| Raison | Explication |
|---|---|
| **Sécurité** | Apache filtre les attaques avant Kestrel (DDoS, SQL injection, XSS) |
| **SSL/TLS** | Apache gère le chiffrement HTTPS, pas besoin de le configurer dans .NET |
| **Ports standards** | Apache écoute sur le port 80/443, Kestrel sur des ports internes (5000, 5001) |
| **VirtualHosts** | Apache peut servir plusieurs sites (.NET ou autres) sur la même IP |
| **Fichiers statiques** | Apache sert les images, CSS, JS plus rapidement que Kestrel |
| **Compression** | Apache compresse les réponses (mod_deflate) |

### Architecture finale

```
┌──────────┐     ┌──────────┐     ┌─────────────────────┐
│  Client   │────►│  Apache  │────►│ Kestrel :5000 (Web) │
│ Navigateur│     │ :80/:443 │     └─────────────────────┘
└──────────┘     │          │
                 │ Reverse  │     ┌─────────────────────┐
┌──────────┐     │  Proxy   │────►│ Kestrel :5001 (API) │
│  Client   │────►│          │     └──────────┬──────────┘
│  API      │     └──────────┘                │
└──────────┘                                   ▼
                                        ┌──────────┐
                                        │  SQLite  │
                                        └──────────┘
```

---

## 2. Configuration des VirtualHosts pour le Reverse Proxy

### Rappel : les VirtualHosts déjà créés

Nous avons déjà créé les fichiers de configuration Apache en Phase 1. Maintenant que nos applications .NET tournent, nous allons les ajuster pour le Reverse Proxy.

### VirtualHost pour `www.nextdev.ne` (Razor Pages)

```bash
sudo nano /etc/apache2/sites-available/www.nextdev.ne.conf
```

```apache
<VirtualHost *:80>
    ServerName www.nextdev.ne
    ServerAlias nextdev.ne

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/www.nextdev.ne_error.log
    CustomLog ${APACHE_LOG_DIR}/www.nextdev.ne_access.log combined

    # Proxy vers Kestrel
    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/

    # En-têtes pour informer Kestrel du vrai client
    ProxyAddHeaders On
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port "80"
    RequestHeader set X-Forwarded-For "%{REMOTE_ADDR}e"

    # Timeouts
    ProxyTimeout 300
    TimeOut 300

    # Sécurité : cacher la signature Apache
    ServerSignature Off
    ServerTokens Prod
</VirtualHost>
```

### VirtualHost pour `api.nextdev.ne` (Minimal API)

```bash
sudo nano /etc/apache2/sites-available/api.nextdev.ne.conf
```

```apache
<VirtualHost *:80>
    ServerName api.nextdev.ne

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/api.nextdev.ne_error.log
    CustomLog ${APACHE_LOG_DIR}/api.nextdev.ne_access.log combined

    # Proxy vers Kestrel
    ProxyPreserveHost On
    ProxyPass / http://localhost:5001/
    ProxyPassReverse / http://localhost:5001/

    # En-têtes
    ProxyAddHeaders On
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port "80"
    RequestHeader set X-Forwarded-For "%{REMOTE_ADDR}e"

    # Timeouts
    ProxyTimeout 300
    TimeOut 300

    # Sécurité
    ServerSignature Off
    ServerTokens Prod

    # Limiter les méthodes HTTP autorisées
    <LimitExcept GET POST PUT DELETE OPTIONS>
        Require all denied
    </LimitExcept>
</VirtualHost>
```

### Recharger Apache

```bash
sudo systemctl reload apache2
```

---

## 3. Test du Reverse Proxy

### Tester le site vitrine via Apache

```bash
# S'assurer que l'application .NET tourne
curl http://localhost:5000

# Tester via Apache avec le bon Host
curl -H "Host: www.nextdev.ne" http://localhost
# Résultat attendu : page HTML complète "Bienvenue sur NextDev"
```

### Tester l'API via Apache

```bash
# Tester directement
curl http://localhost:5001

# Tester via Apache avec le bon Host
curl -H "Host: api.nextdev.ne" http://localhost
# Résultat attendu : JSON { "message": "Bienvenue sur l'API NextDev", ... }

# Tester l'endpoint /trainee via Apache
curl -H "Host: api.nextdev.ne" http://localhost/trainee
# Résultat attendu : JSON avec la liste des stagiaires
```

### Vérifier les logs Apache

```bash
# Voir les accès
sudo tail -f /var/log/apache2/www.nextdev.ne_access.log
sudo tail -f /var/log/apache2/api.nextdev.ne_access.log

# Voir les erreurs
sudo tail -f /var/log/apache2/www.nextdev.ne_error.log
sudo tail -f /var/log/apache2/api.nextdev.ne_error.log
```

---

## 4. Configuration HTTPS avec Let's Encrypt

### Pourquoi HTTPS ?
- **Chiffrement** : les données sont cryptées entre le client et le serveur
- **Confiance** : le cadenas vert rassure les utilisateurs
- **SEO** : Google favorise les sites HTTPS
- **API** : certaines fonctionnalités (geolocalisation, etc.) nécessitent HTTPS

### Installation de Certbot

```bash
sudo apt install -y certbot python3-certbot-apache
```

### Génération des certificats

```bash
# Pour le site vitrine
sudo certbot --apache -d www.nextdev.ne -d nextdev.ne

# Pour l'API
sudo certbot --apache -d api.nextdev.ne
```

Certbot va :
1. Vérifier que nous contrôlons bien les domaines
2. Générer les certificats SSL
3. Modifier automatiquement les VirtualHosts pour ajouter HTTPS
4. Configurer la redirection HTTP → HTTPS

### Vérification des certificats

```bash
# Lister les certificats
sudo certbot certificates

# Vérifier le renouvellement automatique
sudo certbot renew --dry-run
```

### VirtualHosts après Certbot

Certbot génère automatiquement une configuration comme celle-ci :

```apache
<VirtualHost *:443>
    ServerName www.nextdev.ne
    ServerAlias nextdev.ne

    # SSL
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/www.nextdev.ne/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/www.nextdev.ne/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    # Proxy vers Kestrel
    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/

    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Port "443"
</VirtualHost>
```

---

## 5. Configuration de Kestrel côté .NET

Pour que .NET sache qu'il est derrière un Reverse Proxy, il faut configurer le **Forwarded Headers Middleware**.

### Pour le site vitrine

Éditer `Program.cs` du projet Razor Pages :

```bash
cd /home/akaletekoffilevis/Bureau/Challenge/sites/www.nextdev.ne
nano Program.cs
```

```csharp
using Microsoft.AspNetCore.HttpOverrides;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();
builder.WebHost.UseUrls("http://0.0.0.0:5000");

var app = builder.Build();

// Configuration du Forwarded Headers
app.UseForwardedHeaders(new ForwardedHeadersOptions
{
    ForwardedHeaders = ForwardedHeaders.XForwardedFor
                     | ForwardedHeaders.XForwardedProto
                     | ForwardedHeaders.XForwardedHost,
    // Limiter aux proxies de confiance
    KnownProxies = { IPAddress.Parse("127.0.0.1") }
});

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
}

app.UseStaticFiles();
app.UseRouting();
app.MapRazorPages();

app.Run();
```

### Pour l'API

```bash
cd /home/akaletekoffilevis/Bureau/Challenge/sites/api.nextdev.ne
nano Program.cs
```

```csharp
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.EntityFrameworkCore;
using NextDev.Api.Data;
using NextDev.Api.Models;
using System.Net;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Data Source=nextdev.db";
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite(connectionString));

builder.WebHost.UseUrls("http://0.0.0.0:5001");

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Forwarded Headers
app.UseForwardedHeaders(new ForwardedHeadersOptions
{
    ForwardedHeaders = ForwardedHeaders.XForwardedFor
                     | ForwardedHeaders.XForwardedProto
                     | ForwardedHeaders.XForwardedHost,
    KnownProxies = { IPAddress.Parse("127.0.0.1") }
});

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
    DbSeeder.Seed(db);
}

app.UseSwagger();
app.UseSwaggerUI();

// Endpoints...
app.MapGet("/", () => Results.Ok(new { Message = "..." }));
app.MapGet("/trainee", async (AppDbContext db) => { /* ... */ });

app.Run();
```

---

## 6. Optimisations Apache

### Compression Gzip

Activer la compression pour réduire la taille des réponses :

```bash
sudo a2enmod deflate
sudo systemctl reload apache2
```

```bash
sudo nano /etc/apache2/conf-available/compression.conf
```

```apache
<IfModule mod_deflate.c>
    # Compresser les types de contenu textuels
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript
    AddOutputFilterByType DEFLATE application/javascript application/json application/xml

    # Niveau de compression (1-9)
    DeflateCompressionLevel 6

    # Ne pas compresser les petits fichiers
    DeflateBufferSize 8096
</IfModule>
```

```bash
sudo a2enconf compression
sudo systemctl reload apache2
```

### Cache des fichiers statiques

```bash
sudo nano /etc/apache2/conf-available/cache.conf
```

```apache
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 week"
    ExpiresByType text/javascript "access plus 1 week"
    ExpiresByType image/gif "access plus 1 month"
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/png "access plus 1 month"
</IfModule>
```

---

## 7. Script de démarrage complet

Créer un script qui lance tout (Apache + .NET) :

```bash
cd /home/akaletekoffilevis/Bureau/Challenge
nano start-all.sh
```

```bash
#!/bin/bash

echo "=== Démarrage complet du Challenge NextDev ==="

# 1. Apache
echo "[1/4] Vérification d'Apache..."
sudo systemctl start apache2
sudo systemctl status apache2 --no-pager || { echo "ERREUR Apache"; exit 1; }

# 2. DNS
echo "[2/4] Vérification de BIND9..."
sudo systemctl start bind9
sudo systemctl status bind9 --no-pager || { echo "ERREUR DNS"; exit 1; }

# 3. Site Vitrine
echo "[3/4] Démarrage du site vitrine (port 5000)..."
cd /home/akaletekoffilevis/Bureau/Challenge/sites/www.nextdev.ne
dotnet run --configuration Release &
PID_WEB=$!
echo "  PID: $PID_WEB"

# 4. API
echo "[4/4] Démarrage de l'API (port 5001)..."
cd /home/akaletekoffilevis/Bureau/Challenge/sites/api.nextdev.ne
dotnet run --configuration Release &
PID_API=$!
echo "  PID: $PID_API"

# Petit délai pour laisser les applications démarrer
sleep 3

# Test de vérification
echo ""
echo "=== Tests de vérification ==="
curl -o /dev/null -s -w "%{http_code}" http://localhost:5000 && echo " - Site Web OK"
curl -o /dev/null -s -w "%{http_code}" http://localhost:5001 && echo " - API OK"
curl -o /dev/null -s -w "%{http_code}" http://localhost:5001/trainee && echo " - Endpoint /trainee OK"

echo ""
echo "=== Tout est opérationnel ! ==="
echo "Site : http://www.nextdev.ne"
echo "API  : http://api.nextdev.ne"
echo "Stagiaires : http://api.nextdev.ne/trainee"

wait
```

```bash
chmod +x start-all.sh
```

---

## 8. Dépannage (Troubleshooting)

### Problème : "503 Service Unavailable"

**Cause** : .NET n'est pas lancé ou Kestrel n'écoute pas.

**Solution** :
```bash
# Vérifier que .NET tourne
ps aux | grep dotnet

# Vérifier que le port écoute
sudo netstat -tulpn | grep 5000
sudo netstat -tulpn | grep 5001

# Relancer .NET
./start-dotnet.sh
```

### Problème : "403 Forbidden"

**Cause** : Problème de permissions Apache.

**Solution** :
```bash
# Vérifier les logs
sudo tail -f /var/log/apache2/error.log

# Vérifier les permissions
sudo chmod 755 /home/akaletekoffilevis
```

### Problème : "502 Proxy Error"

**Cause** : Apache ne peut pas joindre Kestrel.

**Solution** :
```bash
# Vérifier la configuration du proxy
sudo apachectl configtest

# Vérifier que le module proxy est activé
sudo apachectl -M | grep proxy
```

### Problème : Le Host header ne correspond pas

**Solution** :
```bash
# Vérifier la résolution DNS
dig www.nextdev.ne

# Ajouter dans /etc/hosts si nécessaire
echo "10.0.0.68 www.nextdev.ne api.nextdev.ne" | sudo tee -a /etc/hosts
```

---

## Résumé Phase 3

À la fin de cette phase, nous avons :
- [x] Apache configuré en Reverse Proxy pour les deux sites
- [x] Le site vitrine accessible via `www.nextdev.ne`
- [x] L'API accessible via `api.nextdev.ne`
- [x] HTTPS configuré avec Let's Encrypt (Certbot)
- [x] Forwarded Headers configurés côté .NET
- [x] Compression Gzip activée
- [x] Script `start-all.sh` pour tout lancer en une commande
- [x] Guide de dépannage
