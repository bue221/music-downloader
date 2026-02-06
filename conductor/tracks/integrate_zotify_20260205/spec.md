# Especificación: Integrar Zotify para mejorar la calidad de descarga de Spotify y la organización de la biblioteca

## Descripción
Esta pista tiene como objetivo integrar la herramienta Zotify para mejorar significativamente la calidad de descarga de la música de Spotify y facilitar una mejor organización de la biblioteca local. Esto reemplazará la dependencia actual de búsquedas de YouTube para la descarga de Spotify.

## Objetivos
- Mejorar la calidad de audio de las descargas de Spotify utilizando Zotify.
- Optimizar la organización de la biblioteca local de música.
- Reducir la dependencia de búsquedas en YouTube para contenido de Spotify.

## Requisitos Funcionales
- La aplicación debe ser capaz de descargar canciones y listas de reproducción de Spotify utilizando Zotify.
- Se debe mantener la estructura de carpetas actual para la música descargada.
- Se debe desarrollar un "wrapper" en Python para invocar las funcionalidades de Zotify.

## Requisitos No Funcionales
- **Rendimiento:** Las descargas deben ser eficientes y confiables.
- **Calidad:** La calidad de audio de las descargas debe ser superior a la actual.
- **Mantenibilidad:** El código debe ser modular y fácil de mantener.

## Criterios de Aceptación
- Las canciones de Spotify se descargan en alta calidad utilizando Zotify.
- La organización de archivos por lista de reproducción se mantiene.
- La funcionalidad de descarga de Spotify es estable y no introduce regresiones.

## Pasos Detallados del Usuario (User Stories)
- Como usuario, quiero descargar mi lista de reproducción de Spotify en alta calidad sin depender de YouTube.
- Como usuario, quiero que mis descargas de Spotify se organicen automáticamente en la estructura de carpetas existente.
