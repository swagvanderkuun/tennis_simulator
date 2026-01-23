from __future__ import annotations

from infra.tennis_dagster.code_location.tennis_scraper.tennisexplorer_injuries import (
    parse_injury_table_html,
    to_name_key,
)


def test_to_name_key_basic() -> None:
    assert to_name_key(" Félix   Auger-Aliassime ") == "felix auger aliassime"
    assert to_name_key("  (1)Aryna\u00A0Sabalenka  ") == "aryna sabalenka"


def test_scrape_injury_table_parses_rows_without_profile_enrichment() -> None:
    html = """
    <html><body>
      <table>
        <tr><th>Start</th><th>Name</th><th>Tournament</th><th>Reason</th></tr>
        <tr>
          <td>21.01.2026</td>
          <td><a href="/player/gaston-e1fa4/">Gaston H.</a></td>
          <td>Australian Open</td>
          <td>retired</td>
        </tr>
        <tr>
          <td>19.01.2026</td>
          <td><a href="/player/auger-aliassime/">Auger Aliassime F.</a></td>
          <td>Australian Open</td>
          <td>retired</td>
        </tr>
      </table>
    </body></html>
    """

    rows = parse_injury_table_html(
        html,
        url="https://www.tennisexplorer.com/list-players/injured/",
        status="injured",
        enrich_player_names_from_profiles=False,
    )
    assert len(rows) == 2
    assert rows[0].start_date is not None
    assert rows[0].player_name == "Gaston H."
    assert rows[0].player_profile_url == "https://www.tennisexplorer.com/player/gaston-e1fa4/"
    assert rows[0].tournament == "Australian Open"
    assert rows[0].reason == "retired"
    assert rows[0].player_name_norm == to_name_key("Gaston H.")


