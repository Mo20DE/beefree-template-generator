"""
Email Template Generator mit PydanticAI und OpenAI
Vollständiges Skript zur Generierung von Email-Templates basierend auf dem Simple Template Schema
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, List, Any
from openai import OpenAI
import json
import os
from pathlib import Path


# ============================================================================
# PYDANTIC MODELS - Basierend auf Simple Schema
# ============================================================================

# Module Definitions

class ButtonModule(BaseModel):
    """Button Module für CTAs und Links"""
    type: Literal["button"]
    label: Optional[str] = None
    text: Optional[str] = None
    align: Optional[Literal["left", "center", "right"]] = None
    href: Optional[str] = None
    target: Optional[Literal["_blank", "_self", "_top"]] = None
    size: Optional[int] = Field(None, ge=1)
    color: Optional[str] = None
    background_color: Optional[str] = Field(None, alias="background-color")
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    content_padding_top: Optional[int] = Field(None, ge=0, le=60, alias="contentPaddingTop")
    content_padding_right: Optional[int] = Field(None, ge=0, le=60, alias="contentPaddingRight")
    content_padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="contentPaddingBottom")
    content_padding_left: Optional[int] = Field(None, ge=0, le=60, alias="contentPaddingLeft")
    hover_background_color: Optional[str] = Field(None, alias="hoverBackgroundColor")
    hover_color: Optional[str] = Field(None, alias="hoverColor")
    hover_border_color: Optional[str] = Field(None, alias="hoverBorderColor")
    hover_border_width: Optional[int] = Field(None, ge=0, le=30, alias="hoverBorderWidth")
    border_radius: Optional[int] = Field(None, ge=0, le=60, alias="border-radius")
    border_color: Optional[str] = Field(None, alias="border-color")
    border_width: Optional[int] = Field(None, ge=0, le=30, alias="border-width")
    locked: Optional[bool] = None
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class DividerModule(BaseModel):
    """Divider/Trennlinie Module"""
    type: Literal["divider"]
    color: Optional[str] = None
    height: Optional[int] = Field(None, ge=1, le=30)
    width: Optional[int] = Field(None, ge=1, le=100)
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    locked: Optional[bool] = None
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class HtmlModule(BaseModel):
    """Raw HTML Module"""
    type: Literal["html"]
    html: Optional[str] = None
    locked: Optional[bool] = None
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class Icon(BaseModel):
    """Einzelnes Icon in Icons Module"""
    alt: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    image: str
    href: Optional[str] = None
    height: str
    width: str
    target: Optional[Literal["_blank", "_self", "_top"]] = None
    text_position: Literal["left", "right", "top", "bottom"] = Field(alias="textPosition")

    class Config:
        populate_by_name = True


class IconsModule(BaseModel):
    """Icons/Social Media Module"""
    type: Literal["icons"]
    icons: Optional[List[Icon]] = None
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    locked: Optional[bool] = None
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class ImageModule(BaseModel):
    """Image Module"""
    type: Literal["image"]
    alt: Optional[str] = None
    href: Optional[str] = None
    src: Optional[str] = None
    dynamic_src: Optional[str] = Field(None, alias="dynamicSrc")
    target: Optional[Literal["_blank", "_self", "_top"]] = None
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    locked: Optional[bool] = None
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class ListModule(BaseModel):
    """List Module (ul/ol)"""
    type: Literal["list"]
    underline: Optional[bool] = None
    italic: Optional[bool] = None
    bold: Optional[bool] = None
    html: Optional[str] = None
    text: Optional[str] = None
    align: Optional[Literal["left", "center", "right"]] = None
    tag: Optional[Literal["ol", "ul"]] = None
    size: Optional[int] = Field(None, ge=1)
    color: Optional[str] = None
    link_color: Optional[str] = Field(None, alias="linkColor")
    letter_spacing: Optional[int] = Field(None, ge=-99, le=99, alias="letter-spacing")
    line_height: Optional[float] = Field(None, ge=0.5, le=3, alias="line-height")
    direction: Optional[Literal["ltr", "rtl"]] = None
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    locked: Optional[bool] = None
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class MenuLink(BaseModel):
    """Link in Menu Item"""
    title: Optional[str] = None
    href: Optional[str] = None
    target: Optional[Literal["_blank", "_self", "_top"]] = None


class MenuItem(BaseModel):
    """Menu Item"""
    type: Literal["menu-item"]
    text: Optional[str] = None
    link: Optional[MenuLink] = None


class MenuModule(BaseModel):
    """Navigation Menu Module"""
    type: Literal["menu"]
    items: Optional[List[MenuItem]] = None
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    locked: Optional[bool] = None
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class ParagraphModule(BaseModel):
    """Paragraph/Text Module"""
    type: Literal["paragraph"]
    underline: Optional[bool] = None
    italic: Optional[bool] = None
    bold: Optional[bool] = None
    html: Optional[str] = None
    text: Optional[str] = None
    align: Optional[Literal["left", "center", "right", "justify"]] = None
    size: Optional[int] = Field(None, ge=1)
    color: Optional[str] = None
    link_color: Optional[str] = Field(None, alias="linkColor")
    letter_spacing: Optional[int] = Field(None, ge=-99, le=99, alias="letter-spacing")
    line_height: Optional[float] = Field(None, ge=0.5, le=3, alias="line-height")
    direction: Optional[Literal["ltr", "rtl"]] = None
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    locked: Optional[bool] = None
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class TitleModule(BaseModel):
    """Title/Heading Module"""
    type: Literal["title", "heading"]
    underline: Optional[bool] = None
    italic: Optional[bool] = None
    bold: Optional[bool] = None
    html: Optional[str] = None
    text: Optional[str] = None
    align: Optional[Literal["left", "center", "right", "justify"]] = None
    title: Optional[Literal["h1", "h2", "h3"]] = None
    size: Optional[int] = Field(None, ge=1)
    color: Optional[str] = None
    link_color: Optional[str] = Field(None, alias="linkColor")
    letter_spacing: Optional[int] = Field(None, ge=-99, le=99, alias="letter-spacing")
    line_height: Optional[float] = Field(None, ge=0.5, le=3, alias="line-height")
    direction: Optional[Literal["ltr", "rtl"]] = None
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    locked: Optional[bool] = None
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


# Union Type für alle Module
Module = Union[
    ButtonModule,
    DividerModule,
    HtmlModule,
    IconsModule,
    ImageModule,
    ListModule,
    MenuModule,
    ParagraphModule,
    TitleModule
]


class Column(BaseModel):
    """Spalte in einer Row"""
    weight: int = Field(..., ge=1, le=12, description="Grid weight (1-12)")
    modules: List[Module]
    background_color: Optional[str] = Field(None, alias="background-color")
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    border_color: Optional[str] = Field(None, alias="border-color")
    border_width: Optional[int] = Field(None, ge=0, le=30, alias="border-width")
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class DisplayCondition(BaseModel):
    """Display Condition für conditional rendering"""
    type: str
    label: Optional[str] = None
    description: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None


class Row(BaseModel):
    """Row/Zeile im Template"""
    name: str
    columns: List[Column] = Field(..., min_length=1, max_length=12)
    locked: Optional[bool] = None
    col_stack_on_mobile: Optional[bool] = Field(None, alias="colStackOnMobile")
    row_reverse_col_stack_on_mobile: Optional[bool] = Field(None, alias="rowReverseColStackOnMobile")
    content_area_background_color: Optional[str] = Field(None, alias="contentAreaBackgroundColor")
    background_color: Optional[str] = Field(None, alias="background-color")
    background_image: Optional[str] = Field(None, alias="background-image")
    background_position: Optional[str] = Field(None, alias="background-position")
    background_repeat: Optional[str] = Field(None, alias="background-repeat")
    border_radius: Optional[int] = Field(None, ge=0, le=60, alias="border-radius")
    border_color: Optional[str] = Field(None, alias="border-color")
    border_width: Optional[int] = Field(None, ge=0, le=30, alias="border-width")
    columns_border_radius: Optional[int] = Field(None, ge=0, le=60, alias="columnsBorderRadius")
    columns_spacing: Optional[int] = Field(None, ge=0, le=99, alias="columnsSpacing")
    vertical_align: Optional[Literal["top", "middle", "bottom"]] = Field(None, alias="vertical-align")
    display_condition: Optional[DisplayCondition] = Field(None, alias="display-condition")
    metadata: Optional[dict[str, Any]] = None
    padding_top: Optional[int] = Field(None, ge=0, le=60, alias="padding-top")
    padding_right: Optional[int] = Field(None, ge=0, le=60, alias="padding-right")
    padding_bottom: Optional[int] = Field(None, ge=0, le=60, alias="padding-bottom")
    padding_left: Optional[int] = Field(None, ge=0, le=60, alias="padding-left")
    custom_fields: Optional[dict[str, Any]] = Field(None, alias="customFields")

    class Config:
        populate_by_name = True


class Settings(BaseModel):
    """Template Settings"""
    link_color: Optional[str] = Field(None, alias="linkColor")
    background_color: Optional[str] = Field(None, alias="background-color")
    content_area_background_color: Optional[str] = Field(None, alias="contentAreaBackgroundColor")
    width: Optional[int] = Field(None, ge=320, le=1440)

    class Config:
        populate_by_name = True


class Metadata(BaseModel):
    """Template Metadata"""
    lang: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    preheader: Optional[str] = None


class Template(BaseModel):
    """Main Template Structure"""
    type: Literal["email", "page", "popup"]
    rows: List[Row] = Field(..., min_length=1)
    settings: Optional[Settings] = None
    metadata: Optional[Metadata] = None


class EmailTemplate(BaseModel):
    """Root Email Template Object"""
    template: Template


# ============================================================================
# GENERATOR FUNCTIONS
# ============================================================================

def generate_email_template(
    prompt: str,
    model: str = "gpt-5-mini-2025-08-07"
) -> EmailTemplate:
    """
    Generiert ein Email-Template basierend auf dem Prompt
    
    Args:
        prompt: Beschreibung des gewünschten Templates
        model: OpenAI Model (muss Structured Outputs unterstützen)
    
    Returns:
        EmailTemplate: Validiertes und typisiertes Template
    """
    # OpenAI Client initialisieren
    client = OpenAI(api_key="")
    
    # System Prompt für bessere Ergebnisse
    system_prompt = """Du bist ein Experte für Email-Template-Design.
    
Erstelle professionelle, responsive Email-Templates basierend auf den Anforderungen des Users.

Wichtige Richtlinien:
- Verwende semantisch korrekte Module (title für Überschriften, paragraph für Text, etc.)
- Setze sinnvolle Padding-Werte (typisch 10-20px)
- Verwende professionelle Farben (Hex-Codes)
- Buttons sollten klare CTAs haben
- Images benötigen immer alt-Text
- Berücksichtige Mobile Responsiveness

Standard-Farben:
- Primary: #2563eb (Blue)
- Success: #16a34a (Green)
- Text: #1f2937 (Dark Gray)
- Background: #ffffff (White)
"""
    
    # API Call mit Structured Output
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        response_format=EmailTemplate,
    )
    
    # Parsed Response zurückgeben
    template = completion.choices[0].message.parsed
    
    if template is None:
        raise ValueError("OpenAI konnte kein valides Template generieren")
    
    return template


def save_template_to_file(template: EmailTemplate, filename: str = "template.json"):
    """Speichert das Template als JSON File"""
    output_path = Path(filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            template.model_dump(by_alias=True, exclude_none=True),
            f,
            indent=2,
            ensure_ascii=False
        )
    
    print(f"✅ Template gespeichert: {output_path.absolute()}")


def print_template_summary(template: EmailTemplate):
    """Gibt eine Zusammenfassung des Templates aus"""
    print("\n" + "="*60)
    print("📧 EMAIL TEMPLATE SUMMARY")
    print("="*60)
    
    t = template.template
    print(f"Typ: {t.type}")
    print(f"Anzahl Rows: {len(t.rows)}")
    
    total_modules = sum(
        len(col.modules)
        for row in t.rows
        for col in row.columns
    )
    print(f"Anzahl Module: {total_modules}")
    
    print("\nRow Struktur:")
    for i, row in enumerate(t.rows, 1):
        cols_info = ", ".join(f"{col.weight}/12" for col in row.columns)
        print(f"  {i}. {row.name}: [{cols_info}]")
        
        for j, col in enumerate(row.columns, 1):
            module_types = ", ".join(m.type for m in col.modules)
            print(f"     Col {j}: {module_types}")
    
    if t.settings:
        print(f"\nSettings:")
        if t.settings.width:
            print(f"  Width: {t.settings.width}px")
        if t.settings.background_color:
            print(f"  Background: {t.settings.background_color}")
    
    if t.metadata:
        print(f"\nMetadata:")
        if t.metadata.title:
            print(f"  Title: {t.metadata.title}")
        if t.metadata.subject:
            print(f"  Subject: {t.metadata.subject}")
    
    print("="*60 + "\n")


# ============================================================================
# MAIN FUNCTION & BEISPIELE
# ============================================================================

def main():
    """Hauptfunktion mit Beispielen"""
    
    # # Stelle sicher, dass API Key gesetzt ist
    # if not os.getenv("OPENAI_API_KEY"):
    #     print("❌ Fehler: OPENAI_API_KEY Umgebungsvariable nicht gesetzt!")
    #     print("Setze sie mit: export OPENAI_API_KEY='your-api-key'")
    #     return
    
    # Beispiel 1: Einfaches Welcome Email
    print("Generiere Welcome Email Template...\n")
    
    template = generate_email_template(
        prompt="""
        Erstelle ein professionelles Welcome Email Template für einen SaaS-Service.
        
        Anforderungen:
        - Hero Image mit Logo (Platzhalter URL)
        - Große Überschrift "Welcome to Our Platform!"
        - Kurzer Willkommenstext (2-3 Sätze)
        - CTA Button "Get Started" (blau, zentriert)
        - Divider
        - 3-spaltige Sektion mit Icons für Features (Placeholder Icons)
        - Footer mit Social Media Icons
        
        Design: Modern, clean, professionell
        Farben: Blau (#2563eb) als Primary, weiß als Background
        """
    )
    
    # Summary ausgeben
    print_template_summary(template)
    
    # Als JSON speichern
    save_template_to_file(template, "welcome_email.json")
    
    # Template-Zugriff demonstrieren
    print("🔍 Template Details:")
    print(f"Type: {template.template.type}")
    print(f"First Row Name: {template.template.rows[0].name}")
    print(f"First Module Type: {template.template.rows[0].columns[0].modules[0].type}")
    
    # Beispiel 2: Newsletter Template
    print("\n" + "="*60)
    print("Generiere Newsletter Template...\n")
    
    newsletter = generate_email_template(
        prompt="""
        Erstelle ein Newsletter Template mit folgender Struktur:
        - Header mit Logo links und Social Icons rechts
        - Hero Headline
        - 2 Artikel-Blöcke (Bild links, Text rechts)
        - CTA Button
        - Footer mit Unsubscribe Link
        """
    )
    
    print_template_summary(newsletter)
    save_template_to_file(newsletter, "newsletter.json")
    
    print("\n✅ Alle Templates erfolgreich generiert!")


if __name__ == "__main__":
    main()