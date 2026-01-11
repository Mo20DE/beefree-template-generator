"""
Email Template Generator mit intelligenter Asset-Integration
Unterstützt: Unsplash, DALL-E, Placeholder Services, eigene Assets
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, List, Any
from openai import OpenAI
import json
import os
import requests
from pathlib import Path
from urllib.parse import quote
import base64


# ============================================================================
# ASSET GENERATION & MANAGEMENT
# ============================================================================

class AssetProvider:
    """Base class für Asset Provider"""
    
    def get_image_url(self, description: str, width: int, height: int) -> str:
        raise NotImplementedError


class UnsplashProvider(AssetProvider):
    """Unsplash für hochwertige Stock-Fotos"""
    
    def __init__(self, access_key: Optional[str] = None):
        self.access_key = access_key or os.getenv("UNSPLASH_ACCESS_KEY")
    
    def get_image_url(self, description: str, width: int = 800, height: int = 600) -> str:
        """
        Generiert Unsplash Source URL
        Format: https://source.unsplash.com/{width}x{height}/?{query}
        """
        query = quote(description)
        return f"https://source.unsplash.com/{width}x{height}/?{query}"
    
    def search_specific_image(self, query: str) -> Optional[str]:
        """Sucht spezifisches Bild via Unsplash API"""
        if not self.access_key:
            return None
        
        try:
            response = requests.get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": 1},
                headers={"Authorization": f"Client-ID {self.access_key}"}
            )
            data = response.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
        except Exception as e:
            print(f"⚠️ Unsplash API Error: {e}")
        
        return None


class DALLEProvider(AssetProvider):
    """DALL-E für KI-generierte, maßgeschneiderte Bilder"""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def generate_image(
        self, 
        description: str, 
        size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
        quality: Literal["standard", "hd"] = "standard"
    ) -> str:
        """
        Generiert Bild mit DALL-E 3
        Returns: URL zum generierten Bild
        """
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=description,
                size=size,
                quality=quality,
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            print(f"⚠️ DALL-E Error: {e}")
            return self._fallback_url(description)
    
    def _fallback_url(self, description: str) -> str:
        """Fallback zu Placeholder wenn DALL-E fehlschlägt"""
        return f"https://placehold.co/800x600/2563eb/white?text={quote(description[:30])}"


class PlaceholderProvider(AssetProvider):
    """Placeholder Images für Development/Testing"""
    
    def get_image_url(self, description: str, width: int = 800, height: int = 600) -> str:
        """Generiert Placeholder.co URL"""
        text = quote(description[:50])
        return f"https://placehold.co/{width}x{height}/e5e7eb/1f2937?text={text}"


class CustomAssetLibrary:
    """Verwaltet eigene Asset-Bibliothek"""
    
    def __init__(self, base_url: str = "https://your-cdn.com/assets"):
        self.base_url = base_url
        self.assets = {
            "logos": {
                "primary": f"{base_url}/logo-primary.png",
                "white": f"{base_url}/logo-white.png",
                "icon": f"{base_url}/logo-icon.png",
            },
            "social": {
                "facebook": f"{base_url}/social/facebook.png",
                "twitter": f"{base_url}/social/twitter.png",
                "instagram": f"{base_url}/social/instagram.png",
                "linkedin": f"{base_url}/social/linkedin.png",
            },
            "banners": {
                "hero": f"{base_url}/banners/hero.jpg",
                "promo": f"{base_url}/banners/promo.jpg",
            }
        }
    
    def get_logo(self, variant: str = "primary") -> str:
        return self.assets["logos"].get(variant, self.assets["logos"]["primary"])
    
    def get_social_icon(self, platform: str) -> str:
        return self.assets["social"].get(platform.lower(), "")
    
    def get_banner(self, type: str = "hero") -> str:
        return self.assets["banners"].get(type, "")


class AssetManager:
    """Zentrale Asset-Verwaltung mit Multi-Provider Support"""
    
    def __init__(
        self,
        openai_client: OpenAI,
        strategy: Literal["unsplash", "dalle", "placeholder", "mixed"] = "mixed",
        custom_library: Optional[CustomAssetLibrary] = None
    ):
        self.unsplash = UnsplashProvider()
        self.dalle = DALLEProvider(openai_client)
        self.placeholder = PlaceholderProvider()
        self.custom = custom_library or CustomAssetLibrary()
        self.strategy = strategy
    
    def get_image(
        self, 
        description: str, 
        width: int = 800, 
        height: int = 600,
        use_ai: bool = False
    ) -> str:
        """
        Holt Bild basierend auf Strategie
        
        Args:
            description: Beschreibung des gewünschten Bildes
            width: Bildbreite
            height: Bildhöhe
            use_ai: Wenn True, nutze DALL-E für generierte Bilder
        """
        if use_ai and self.strategy in ["dalle", "mixed"]:
            size = self._get_dalle_size(width, height)
            return self.dalle.generate_image(description, size=size)
        
        if self.strategy == "unsplash":
            return self.unsplash.get_image_url(description, width, height)
        
        if self.strategy == "placeholder":
            return self.placeholder.get_image_url(description, width, height)
        
        # Mixed: Versuche Unsplash, fallback zu Placeholder
        url = self.unsplash.search_specific_image(description)
        return url or self.placeholder.get_image_url(description, width, height)
    
    def get_logo(self, variant: str = "primary") -> str:
        """Holt Logo aus Custom Library"""
        return self.custom.get_logo(variant)
    
    def get_social_icons(self, platforms: List[str]) -> dict[str, str]:
        """Holt Social Media Icons"""
        return {
            platform: self.custom.get_social_icon(platform)
            for platform in platforms
        }
    
    def _get_dalle_size(self, width: int, height: int) -> Literal["1024x1024", "1792x1024", "1024x1792"]:
        """Konvertiert Dimensionen zu DALL-E Größe"""
        ratio = width / height
        if ratio > 1.5:
            return "1792x1024"  # Landscape
        elif ratio < 0.7:
            return "1024x1792"  # Portrait
        return "1024x1024"  # Square


# ============================================================================
# ERWEITERTE TEMPLATE GENERATION MIT ASSETS
# ============================================================================

# [Hier würden die Pydantic Models aus dem vorherigen Skript eingefügt]
# Für Kürze importiere ich sie hier symbolisch:

class Module(BaseModel):
    """Basis Module (vereinfacht)"""
    type: str

class ImageModule(Module):
    """Image Module mit Asset-Support"""
    type: Literal["image"]
    src: str
    alt: str
    href: Optional[str] = None
    target: Optional[Literal["_blank", "_self", "_top"]] = None

class ButtonModule(Module):
    """Button Module"""
    type: Literal["button"]
    text: str
    href: str
    background_color: Optional[str] = Field(None, alias="background-color")

class Column(BaseModel):
    weight: int
    modules: List[Union[ImageModule, ButtonModule, Module]]

class Row(BaseModel):
    name: str
    columns: List[Column]

class Template(BaseModel):
    type: Literal["email", "page", "popup"]
    rows: List[Row]

class EmailTemplate(BaseModel):
    template: Template


def generate_template_with_assets(
    prompt: str,
    openai_client: OpenAI,
    asset_manager: AssetManager,
    model: str = "gpt-4o-2024-08-06"
) -> tuple[EmailTemplate, dict[str, str]]:
    """
    Generiert Template und resolved Assets intelligent
    
    Returns:
        (template, asset_map): Template mit Placeholder + Map von Beschreibung zu URL
    """
    
    # Schritt 1: Template mit Asset-Beschreibungen generieren
    system_prompt = """Du bist ein Email-Template Designer mit Asset-Integration.

Erstelle Templates mit Bild-Beschreibungen, die später durch echte Assets ersetzt werden.

Für Bilder:
- Nutze beschreibende Texte in src: "hero-image-modern-office"
- Setze aussagekräftige alt-Texte
- Verwende src="logo-primary" für Logos
- Verwende src="social-{platform}" für Social Icons (z.B. "social-facebook")

Beispiel:
{
  "type": "image",
  "src": "hero-tech-startup",
  "alt": "Modern tech startup office with team collaboration"
}
"""
    
    # Template generieren (mit Placeholder-Beschreibungen)
    completion = openai_client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        response_format=EmailTemplate,
    )
    
    template = completion.choices[0].message.parsed
    
    if not template:
        raise ValueError("Template konnte nicht generiert werden")
    
    # Schritt 2: Asset-Descriptions sammeln und resolven
    asset_map = {}
    
    def resolve_assets(obj):
        """Recursive function um Assets zu finden und zu resolven"""
        if isinstance(obj, ImageModule):
            description = obj.src
            
            # Spezielle Keywords erkennen
            if description.startswith("logo-"):
                variant = description.replace("logo-", "")
                asset_map[description] = asset_manager.get_logo(variant)
            elif description.startswith("social-"):
                platform = description.replace("social-", "")
                asset_map[description] = asset_manager.get_social_icons([platform])[platform]
            else:
                # Normales Bild via Asset Manager
                use_ai = "custom" in description or "generate" in description.lower()
                asset_map[description] = asset_manager.get_image(
                    obj.alt or description,
                    use_ai=use_ai
                )
            
            # URL im Template ersetzen
            obj.src = asset_map[description]
        
        elif isinstance(obj, list):
            for item in obj:
                resolve_assets(item)
        elif hasattr(obj, '__dict__'):
            for value in obj.__dict__.values():
                resolve_assets(value)
    
    # Assets resolven
    resolve_assets(template)
    
    return template, asset_map


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_unsplash_template():
    """Beispiel: Template mit Unsplash Bildern"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    asset_manager = AssetManager(
        openai_client=client,
        strategy="unsplash"
    )
    
    template, assets = generate_template_with_assets(
        prompt="""
        Erstelle ein Product Launch Email:
        - Hero image: Moderne Tech-Produkt Präsentation
        - Logo im Header
        - 3 Feature-Bilder: "collaboration", "security", "analytics"
        - CTA Button
        - Social Icons im Footer
        """,
        openai_client=client,
        asset_manager=asset_manager
    )
    
    print("✅ Template mit Unsplash Bildern erstellt!")
    print(f"📸 Assets resolved: {len(assets)}")
    for desc, url in assets.items():
        print(f"  {desc} → {url[:60]}...")
    
    return template


def example_dalle_template():
    """Beispiel: Template mit DALL-E generierten Bildern"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    asset_manager = AssetManager(
        openai_client=client,
        strategy="dalle"
    )
    
    template, assets = generate_template_with_assets(
        prompt="""
        Erstelle ein Fantasy Newsletter:
        - GENERATE: Hero Banner mit magischem Schloss bei Sonnenuntergang
        - GENERATE: Icon für "Magic Spells" (mystisches Symbol)
        - GENERATE: Icon für "Potions" (Zaubertrank)
        - Logo
        - Social Icons
        """,
        openai_client=client,
        asset_manager=asset_manager
    )
    
    print("✅ Template mit DALL-E Bildern erstellt!")
    print(f"🎨 AI-generierte Assets: {len([k for k in assets if 'generate' in k.lower()])}")
    
    return template


def example_mixed_strategy():
    """Beispiel: Mixed Strategy - beste Assets aus allen Quellen"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Custom Asset Library konfigurieren
    custom_lib = CustomAssetLibrary(base_url="https://cdn.mycompany.com")
    
    asset_manager = AssetManager(
        openai_client=client,
        strategy="mixed",
        custom_library=custom_lib
    )
    
    template, assets = generate_template_with_assets(
        prompt="""
        Erstelle Corporate Newsletter:
        - Company Logo (verwende eigenes Logo)
        - Hero: Büro-Teamwork (Unsplash)
        - GENERATE: Custom Illustration für neue Feature
        - Product Screenshots (Placeholder für jetzt)
        - Social Media Icons (eigene Icons)
        """,
        openai_client=client,
        asset_manager=asset_manager
    )
    
    print("✅ Template mit Mixed Strategy erstellt!")
    print(f"📦 Asset Sources:")
    print(f"  - Custom Library: {len([k for k in assets if 'logo' in k or 'social' in k])}")
    print(f"  - Unsplash: {len([k for k in assets if 'unsplash' in assets[k]])}")
    print(f"  - DALL-E: {len([k for k in assets if 'oaidalleapiprodscus' in assets[k]])}")
    print(f"  - Placeholder: {len([k for k in assets if 'placehold' in assets[k]])}")
    
    return template


def save_with_asset_metadata(template: EmailTemplate, assets: dict, filename: str):
    """Speichert Template mit Asset-Metadaten"""
    output = {
        "template": template.model_dump(by_alias=True, exclude_none=True),
        "assets": {
            "count": len(assets),
            "urls": assets,
            "generated_at": "2025-01-10T12:00:00Z"
        }
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Template + Assets gespeichert: {filename}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Hauptfunktion mit verschiedenen Asset-Strategien"""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Fehler: OPENAI_API_KEY nicht gesetzt!")
        return
    
    print("🎨 Email Template Generator mit Asset-Integration\n")
    print("Verfügbare Strategien:")
    print("  1. Unsplash - Hochwertige Stock-Fotos")
    print("  2. DALL-E - AI-generierte Custom Bilder")
    print("  3. Mixed - Beste Assets aus allen Quellen")
    print("  4. Placeholder - Für schnelles Prototyping\n")
    
    # Beispiel ausführen
    print("Führe Mixed Strategy Beispiel aus...\n")
    
    template = example_mixed_strategy()
    
    print("\n" + "="*60)
    print("💡 KOSTEN-ÜBERSICHT")
    print("="*60)
    print("Unsplash: KOSTENLOS (bis 50 requests/hour)")
    print("DALL-E 3 Standard: $0.040 pro Bild")
    print("DALL-E 3 HD: $0.080 pro Bild")
    print("Structured Output: Keine extra Kosten")
    print("="*60)


if __name__ == "__main__":
    main()