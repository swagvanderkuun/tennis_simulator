#!/usr/bin/env python3
"""
Tennis Simulator CLI

Command-line interface for the tennis tournament simulator.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
import json
import os

from src.tennis_simulator import (
    FixedDrawSimulator, run_tournament_simulation,
    player_db, PlayerSelector, Gender, Tier
)

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Tennis Tournament Simulator CLI"""
    pass


@cli.command()
@click.option('--gender', '-g', type=click.Choice(['men', 'women', 'both']), default='both', 
              help='Gender to list players for')
@click.option('--tier', '-t', type=click.Choice(['A', 'B', 'C', 'D']), 
              help='Filter by tier')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'simple']), default='table',
              help='Output format')
def list_players(gender, tier, format):
    """List all players in the database"""
    
    if format == 'json':
        # JSON output
        players_data = {}
        
        if gender in ['men', 'both']:
            men_players = player_db.get_players_by_gender(Gender.MEN)
            if tier:
                men_players = {k: v for k, v in men_players.items() if v.tier == Tier(tier)}
            players_data['men'] = {name: player.to_dict() for name, player in men_players.items()}
        
        if gender in ['women', 'both']:
            women_players = player_db.get_players_by_gender(Gender.WOMEN)
            if tier:
                women_players = {k: v for k, v in women_players.items() if v.tier == Tier(tier)}
            players_data['women'] = {name: player.to_dict() for name, player in women_players.items()}
        
        console.print_json(json.dumps(players_data, indent=2))
        return
    
    # Table output
    if gender in ['men', 'both']:
        console.print(Panel.fit(f"[bold blue]Men's Players[/bold blue]", border_style="blue"))
        
        if format == 'table':
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Tier", style="green")
            table.add_column("Country", style="yellow")
            table.add_column("Elo", style="red")
            table.add_column("yElo", style="red")
            table.add_column("Rank", style="blue")
            
            men_players = player_db.get_players_by_gender(Gender.MEN)
            if tier:
                men_players = {k: v for k, v in men_players.items() if v.tier == Tier(tier)}
            
            for name, player in sorted(men_players.items()):
                table.add_row(
                    name,
                    player.tier.value,
                    player.country,
                    str(player.elo) if player.elo else "N/A",
                    str(player.yelo) if player.yelo else "N/A",
                    str(player.rank) if player.rank else "N/A"
                )
            
            console.print(table)
        else:
            for name, player in sorted(men_players.items()):
                console.print(f"{name} ({player.tier.value}) - {player.country}")
    
    if gender in ['women', 'both']:
        console.print(Panel.fit(f"[bold pink]Women's Players[/bold pink]", border_style="pink"))
        
        if format == 'table':
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Tier", style="green")
            table.add_column("Country", style="yellow")
            table.add_column("Elo", style="red")
            table.add_column("yElo", style="red")
            table.add_column("Rank", style="blue")
            
            women_players = player_db.get_players_by_gender(Gender.WOMEN)
            if tier:
                women_players = {k: v for k, v in women_players.items() if v.tier == Tier(tier)}
            
            for name, player in sorted(women_players.items()):
                table.add_row(
                    name,
                    player.tier.value,
                    player.country,
                    str(player.elo) if player.elo else "N/A",
                    str(player.yelo) if player.yelo else "N/A",
                    str(player.rank) if player.rank else "N/A"
                )
            
            console.print(table)
        else:
            for name, player in sorted(women_players.items()):
                console.print(f"{name} ({player.tier.value}) - {player.country}")


@cli.command()
@click.option('--simulations', '-s', default=1000, help='Number of simulations to run')
@click.option('--tournament', '-t', default='Wimbledon', help='Tournament name')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
def simulate(simulations, tournament, output):
    """Run tournament simulations using fixed draw data"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running simulations...", total=None)
        
        # Run simulations
        simulator = run_tournament_simulation(
            num_simulations=simulations,
            tournament_name=tournament
        )
        
        progress.update(task, description="Simulations completed!")
    
    # Save results if output file specified
    if output:
        results = {
            "tournament": tournament,
            "simulations": simulations,
            "results": simulator.simulation_results
        }
        
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        
        console.print(f"[green]Results saved to {output}[/green]")


@cli.command()
@click.option('--gender', '-g', type=click.Choice(['men', 'women']), required=True, 
              help='Gender to get recommendations for')
@click.option('--tier', '-t', type=click.Choice(['A', 'B', 'C', 'D']), required=True,
              help='Tier to get recommendations for')
@click.option('--count', '-c', default=5, help='Number of recommendations')
@click.option('--simulations', '-s', default=1000, help='Number of simulations for analysis')
def recommend(gender, tier, count, simulations):
    """Get player recommendations for a specific tier"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running simulations for recommendations...", total=None)
        
        # Run simulations first
        simulator = run_tournament_simulation(
            num_simulations=simulations,
            tournament_name="Wimbledon"
        )
        
        progress.update(task, description="Getting recommendations...")
        
        # Get recommendations
        recommendations = simulator.get_player_recommendations(
            Gender.MEN if gender == 'men' else Gender.WOMEN,
            Tier(tier),
            count
        )
        
        progress.update(task, description="Recommendations ready!")
    
    # Display recommendations
    console.print(Panel.fit(
        f"[bold]Top {count} {gender.title()} {tier}-Tier Recommendations[/bold]",
        border_style="green"
    ))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="cyan")
    table.add_column("Player", style="green")
    table.add_column("Win Rate", style="red")
    table.add_column("Final Rate", style="yellow")
    table.add_column("SF Rate", style="blue")
    table.add_column("QF Rate", style="magenta")
    table.add_column("Expected Points", style="bold white")
    
    for i, (player, stats) in enumerate(recommendations, 1):
        table.add_row(
            str(i),
            player.name,
            f"{stats['win_rate']:.1f}%",
            f"{stats['final_rate']:.1f}%",
            f"{stats['semifinal_rate']:.1f}%",
            f"{stats['quarterfinal_rate']:.1f}%",
            f"{stats['expected_points']:.1f}"
        )
    
    console.print(table)


@cli.command()
@click.option('--gender', '-g', type=click.Choice(['men', 'women', 'both']), default='both',
              help='Gender to select players for')
@click.option('--save', '-s', type=click.Path(), help='Save selections to file')
@click.option('--load', '-l', type=click.Path(), help='Load selections from file')
def select(gender, save, load):
    """Interactive player selection"""
    
    if load and os.path.exists(load):
        with open(load, 'r') as f:
            selections = json.load(f)
        
        console.print(f"[green]Loaded selections from {load}[/green]")
        
        # Display loaded selections
        for g, players in selections.items():
            console.print(Panel.fit(f"[bold]{g.title()} Selections[/bold]", border_style="blue"))
            for tier, player_list in players.items():
                console.print(f"{tier}: {', '.join(player_list)}")
        
        return
    
    # Run interactive selector
    selections = run_interactive_selector(gender)
    
    if save:
        with open(save, 'w') as f:
            json.dump(selections, f, indent=2)
        
        console.print(f"[green]Selections saved to {save}[/green]")


@cli.command()
@click.argument('selections_file', type=click.Path(exists=True))
@click.option('--simulations', '-s', default=1000, help='Number of simulations for analysis')
def analyze(selections_file, simulations):
    """Analyze player selections"""
    
    with open(selections_file, 'r') as f:
        selections = json.load(f)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running simulations for analysis...", total=None)
        
        # Run simulations
        simulator = run_tournament_simulation(
            num_simulations=simulations,
            tournament_name="Wimbledon"
        )
        
        progress.update(task, description="Analyzing selections...")
        
        # Analyze selections
        total_points = 0
        analysis = {}
        
        for gender, tier_players in selections.items():
            analysis[gender] = {}
            gender_points = 0
            
            for tier, players in tier_players.items():
                tier_points = 0
                tier_analysis = []
                
                for player_name in players:
                    # Find player in database
                    all_players = player_db.get_players_by_gender(
                        Gender.MEN if gender == 'men' else Gender.WOMEN
                    )
                    
                    if player_name in all_players:
                        player = all_players[player_name]
                        
                        # Get player performance from simulations
                        wins = 0
                        finals = 0
                        semifinals = 0
                        quarterfinals = 0
                        
                        for result in simulator.simulation_results:
                            if gender == 'men':
                                if result["men_winner"] == player_name:
                                    wins += 1
                                if player_name in result["men_finalists"]:
                                    finals += 1
                                if player_name in result["men_semifinalists"]:
                                    semifinals += 1
                                if player_name in result["men_quarterfinalists"]:
                                    quarterfinals += 1
                            else:
                                if result["women_winner"] == player_name:
                                    wins += 1
                                if player_name in result["women_finalists"]:
                                    finals += 1
                                if player_name in result["women_semifinalists"]:
                                    semifinals += 1
                                if player_name in result["women_quarterfinalists"]:
                                    quarterfinals += 1
                        
                        expected_points = (wins * 32 + finals * 16 + semifinals * 8 + quarterfinals * 4) / simulations
                        tier_points += expected_points
                        
                        tier_analysis.append({
                            "player": player_name,
                            "expected_points": expected_points,
                            "win_rate": wins / simulations * 100,
                            "final_rate": finals / simulations * 100
                        })
                
                analysis[gender][tier] = {
                    "players": tier_analysis,
                    "total_points": tier_points
                }
                gender_points += tier_points
            
            analysis[gender]["total_points"] = gender_points
            total_points += gender_points
        
        analysis["total_points"] = total_points
        
        progress.update(task, description="Analysis complete!")
    
    # Display analysis
    console.print(Panel.fit(f"[bold]Selection Analysis[/bold]", border_style="green"))
    console.print(f"Total Expected Points: [bold]{total_points:.1f}[/bold]")
    
    for gender, gender_data in analysis.items():
        if gender == "total_points":
            continue
            
        console.print(f"\n[bold]{gender.title()}[/bold] - {gender_data['total_points']:.1f} points")
        
        for tier, tier_data in gender_data.items():
            if tier == "total_points":
                continue
                
            console.print(f"  {tier}: {tier_data['total_points']:.1f} points")
            
            for player_analysis in tier_data['players']:
                console.print(f"    {player_analysis['player']}: {player_analysis['expected_points']:.1f} points "
                            f"({player_analysis['win_rate']:.1f}% win, {player_analysis['final_rate']:.1f}% final)")


@cli.command()
def stats():
    """Show database statistics"""
    
    men_players = player_db.get_players_by_gender(Gender.MEN)
    women_players = player_db.get_players_by_gender(Gender.WOMEN)
    
    # Count by tier
    men_tiers = {}
    women_tiers = {}
    
    for player in men_players.values():
        tier = player.tier.value
        men_tiers[tier] = men_tiers.get(tier, 0) + 1
    
    for player in women_players.values():
        tier = player.tier.value
        women_tiers[tier] = women_tiers.get(tier, 0) + 1
    
    console.print(Panel.fit("[bold]Database Statistics[/bold]", border_style="blue"))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    
    table.add_row("Total Men", str(len(men_players)))
    table.add_row("Total Women", str(len(women_players)))
    table.add_row("Total Players", str(len(men_players) + len(women_players)))
    
    for tier in ['A', 'B', 'C', 'D']:
        table.add_row(f"Men {tier}-Tier", str(men_tiers.get(tier, 0)))
        table.add_row(f"Women {tier}-Tier", str(women_tiers.get(tier, 0)))
    
    console.print(table)


if __name__ == '__main__':
    cli() 