using System.ComponentModel.DataAnnotations;
namespace NextDev.Api.Models;
public class Trainee
{
    public int Id { get; set; }
    [Required][MaxLength(100)] public string Nom { get; set; } = string.Empty;
    [Required][MaxLength(100)] public string Prenom { get; set; } = string.Empty;
    [Required][EmailAddress][MaxLength(200)] public string Email { get; set; } = string.Empty;
    [DataType(DataType.Date)] public DateTime DateNaissance { get; set; }
    public DateTime DateInscription { get; set; } = DateTime.UtcNow;
}
