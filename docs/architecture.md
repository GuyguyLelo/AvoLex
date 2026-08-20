# Architecture AvoLex

## Vue d'ensemble

AvoLex est un SaaS multi-tenant (colonne `cabinet`) pour la gestion de cabinets d'avocats.

## Stack

- Python 3.12, Django 5.x
- PostgreSQL 16
- Redis + Celery
- Templates Django + CSS/JS vanilla
- WeasyPrint (PDF)

## Structure

Voir le `README.md` racine. Les apps métier vivent sous `apps/`.

## Multi-tenancy

Introduit à l'étape 2 : `TenantOwnedModel`, middleware, managers filtrants.

## UI (étape 3)

- CSS : `static/css/base.css` (tokens), `components.css`, `layout.css`, `landing.css`
- JS : ES modules (`static/js/main.js` + `modules/`)
- Layouts : `templates/layouts/app.html`, `public.html`, `auth.html`
- Partials : sidebar, topbar, breadcrumb, messages

## Environnement local

Pas de Docker : PostgreSQL et Redis installés nativement (ou services managés).
Voir `README.md` pour l'installation.
