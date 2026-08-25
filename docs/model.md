# Dictionnaire de données AvoLex

## Convention

- Code / champs : anglais
- `verbose_name` / UI : français
- PK : UUID v4 (`BaseModel`)
- Soft-delete : `is_deleted`, `deleted_at` (manager par défaut exclut les supprimés)
- Multi-tenant : modèles métier héritent de `TenantOwnedModel` (`cabinet` FK)

## `accounts.User`

| Champ | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| email | Email unique | Identifiant (`USERNAME_FIELD`) |
| first_name, last_name | Char | |
| is_staff, is_active, is_superuser | Bool | |
| date_joined | DateTime | |
| timezone | Char | défaut `Europe/Paris` |
| locale | Char | défaut `fr` |

## `tenants.Cabinet`

Tenant racine (n'hérite pas de `TenantOwnedModel`).

| Champ | Type | Notes |
|-------|------|-------|
| name, slug | Char / Slug | slug unique |
| legal_name, siret, vat_number, bar_association | Char | mentions légales |
| address_*, city, postal_code, country | Char | country ISO-2, défaut FR |
| default_currency | Char(3) | EUR |
| retention_days | Int | RGPD, défaut 3650 |
| is_active | Bool | |

## `tenants.Membership`

| Champ | Type | Notes |
|-------|------|-------|
| cabinet | FK Cabinet | |
| user | FK User | |
| role | Char | owner, lawyer, associate, secretary, read_only |
| is_active | Bool | |
| Contrainte | unique (cabinet, user) si non soft-deleted | |

## `tenants.Invitation`

| Champ | Type | Notes |
|-------|------|-------|
| cabinet | FK | |
| email | Email | |
| role | Char | ≠ owner |
| token | Char unique | URL-safe |
| invited_by | FK User | |
| expires_at | DateTime | +7 jours |
| accepted_at | DateTime nullable | |

## `tenants.CabinetPreference` (TenantOwned)

Préférences clé/valeur JSON ; sert aussi de canari d'isolation multi-tenant.

## Rôles → permissions

| Permission | Owner | Avocat | Collaborateur | Secrétaire | Lecture seule |
|------------|-------|--------|---------------|------------|---------------|
| view | ✓ | ✓ | ✓ | ✓ | ✓ |
| add / change | ✓ | ✓ | ✓ | ✓ | |
| delete | ✓ | ✓ | | | |
| invite | ✓ | ✓ | | | |
| manage_members / billing / cabinet | ✓ | | | | |

## `clients.Client` (TenantOwned)

Personne physique / morale — CRUD UI `/clients/`, recherche + pagination.

## `matters.Matter` (TenantOwned)

Dossier avec `reference` unique `DOS-YYYY-NNNNN`, client, avocat responsable, statut.

## `matters.MatterAction` (TenantOwned)

Historique d'actions (`created`, `updated`, `status_changed`, `deleted`).

## `calendar_app.Event` (TenantOwned)

Audiences, RDV, délais, rappels, tâches (`is_done`, `remind_at`).

## `documents.Document` (TenantOwned)

| Champ | Type | Notes |
|-------|------|-------|
| matter | FK Matter | |
| title, description | Char / Text | |
| tags | ArrayField[str] | tags normalisés |
| current_version | FK DocumentVersion | nullable |

## `documents.DocumentVersion` (TenantOwned)

| Champ | Type | Notes |
|-------|------|-------|
| document | FK Document | |
| version_number | Int | unique par document |
| file | FileField | storage privé `private_media/documents/` |
| original_filename | Char | |
| checksum | SHA-256 | |
| size, mime_type | | |
| uploaded_by | FK User | |

⚠️ Aucune URL publique : téléchargement / aperçu uniquement via vues authentifiées.

## `billing.TimeEntry` (TenantOwned)

| Champ | Type | Notes |
|-------|------|-------|
| matter | FK Matter | |
| user | FK User | auteur de la saisie |
| description | Char | |
| started_at, ended_at | DateTime | timer ; manuelle peut les renseigner |
| duration_minutes | Int | |
| hourly_rate | Decimal | EUR |
| is_billable | Bool | |
| invoice | FK Invoice | nullable jusqu'à facturation |

Montant HT = `duration_minutes / 60 * hourly_rate`.

## `billing.Expense` (TenantOwned)

| Champ | Type | Notes |
|-------|------|-------|
| matter | FK Matter | |
| description | Char | |
| amount | Decimal | EUR HT |
| incurred_on | Date | |
| is_billable | Bool | |
| invoice | FK Invoice | nullable |

## `billing.Invoice` (TenantOwned)

| Champ | Type | Notes |
|-------|------|-------|
| client, matter | FK | matter optionnel |
| number | Char | `FAC-YYYY-NNNNN` à l'émission ; unique par cabinet |
| status | Char | draft, sent, paid, overdue, cancelled |
| issued_at, due_date, paid_at | Date/DateTime | |
| tax_rate | Decimal | % |
| subtotal, tax_amount, total | Decimal | calculés |
| pdf | FileField | storage privé `private_media/invoices/` |

## `billing.InvoiceSequence` (TenantOwned)

Compteur annuel par cabinet (`year`, `last_number`) — allocation sous `SELECT FOR UPDATE`.

## `billing.InvoiceLine` (TenantOwned)

Ligne figée (temps / débours / manuel) avec quantités, prix unitaires et montants HT.

*(Dictionnaire étendu abonnements…)*
