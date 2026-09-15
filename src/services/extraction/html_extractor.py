"""
Script d'extraction des documents HTML.
"""

from bs4 import BeautifulSoup


def promote_summary_to_heading(html_content: str, heading_tag: str = "h3") -> str:
    """
    Transforme chaque <summary> à l'intérieur d'un <details> en une vraie
    balise de titre HTML (h3 dans notre cas), pour que Docling la reconnaisse
    nativement comme titre de sous-partie et non pas comme le texte contenu dans
    le <p>.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    for summary in soup.find_all("summary"):
        heading = soup.new_tag(heading_tag)
        heading.string = summary.get_text(strip=True)
        summary.replace_with(heading)

    for details in soup.find_all("details"):
        details.unwrap()

    return str(soup)
