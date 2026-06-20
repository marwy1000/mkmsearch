import typer
from typer.core import TyperGroup
APP_VERSION = "0.4.0"


class CustomHelpCommandGroup(TyperGroup):
    def format_help(self, ctx, formatter):
        """
        Customize help output to include -h as an alias for --help.
        """
        super().format_help(ctx, formatter)

    def parse_args(self, ctx, args):
        # Replace `-h` with `--help` before parsing arguments
        if "-h" in args and "--help" not in args:
            args[args.index("-h")] = "--help"
        super().parse_args(ctx, args)

app = typer.Typer(cls=CustomHelpCommandGroup, add_completion=False)

@app.command()
def download(
    year: int = typer.Option(None, "-y", "--year", help="The year of the report to download"),
    month: int = typer.Option(None, "-m", "--month", help="The month of the report to download")
):
    """
    Downloads all reports from CM that have been generated, doesn't download them again by checking what has been downloaded. Specify year and month to redownload 1 report.
    """
    from src.downloads import download_reports
    download_reports(year, month)

from src.search import (product_name_column, quantity_column, quality_column, foiliness_column, 
    set_name_column, language_column, date_of_purchase_column, user_name_column,
    user_name_column, order_id_column, shipment_cost_column, total_price_column)

default_columns_1 = f"{product_name_column},{quantity_column},{quality_column},{foiliness_column}"
default_columns_2 = f"{product_name_column},{set_name_column},{quantity_column},{quality_column},{language_column},{foiliness_column},Price,{date_of_purchase_column}"
default_columns_3 = f"{product_name_column},{set_name_column},{quantity_column},Price,{date_of_purchase_column},{user_name_column},{order_id_column}"
default_columns_4 = f"{set_name_column},{product_name_column},{user_name_column},{order_id_column},{quantity_column},{total_price_column},Price,{date_of_purchase_column}"
default_columns_5 = f"{user_name_column},{order_id_column},{shipment_cost_column},{total_price_column},Price,{date_of_purchase_column}"

display_columns_help_1 = f"The default option for which columns to show. You can also customize what to show. Columns: {default_columns_1}"
display_columns_help_2 = f"Columns: {default_columns_2}"
display_columns_help_3 = f"Columns: {default_columns_3}"
display_columns_help_4 = f"Columns: {default_columns_4}"
display_columns_help_5 = f"Columns: {default_columns_5}"
date_of_purchase_help= 'The date of purchase as "YYYY-MM-DD". Prefix with ">" or "<" or type "YYYY-MM-DD to YYYY-MM-DD".'
@app.command()
def search(
    product_name: str = typer.Option(None, "-p", "--product-name", help="The name of the product to search for."),
    set_name: str = typer.Option(None, "-s", "--set-name", help="The name of the set to filter for."),
    user_name: str = typer.Option(None, "-u", "--user-name", help="The user name of the seller."),
    date_of_purchase: str = typer.Option(None, "-d", "--date-of-purchase", help=date_of_purchase_help),
    foiliness: bool = typer.Option(False, "-f", "--foil", help="Show only foils."),
    sort_by: str = typer.Option("Product Name", "-sb", "--sort-by", help="Column name to sort by (e.g., 'Product Name', 'Price')."),
    sort_order: bool = typer.Option(False, "-asc", "--ascending", help="Use this option to sort in ascending order."),
    default_columns_1: bool = typer.Option(False, "-1", "--1", help=display_columns_help_1),
    default_columns_2: bool = typer.Option(False, "-2", "--2", help=display_columns_help_2),
    default_columns_3: bool = typer.Option(False, "-3", "--3", help=display_columns_help_3),
    default_columns_4: bool = typer.Option(False, "-4", "--4", help=display_columns_help_4),
    default_columns_5: bool = typer.Option(False, "-5", "--5", help=display_columns_help_5),
    limit: int = typer.Option(100, "-l", "--limit", help="Limit the number of rows displayed in the results.")
):
    """
    Search and format the order details with optional filtering, sorting, grouping, and summarization.
    """
    from src.search import search
    if (default_columns_1):
        display_columns = 1
    elif (default_columns_2):
        display_columns = 2
    elif (default_columns_3):
        display_columns = 3
    elif (default_columns_4):
        display_columns = 4
    elif (default_columns_5):
        display_columns = 5
    else:
        display_columns = 1

    search(product_name, set_name, user_name, date_of_purchase, foiliness, sort_by, sort_order, display_columns, limit)

@app.command()
def generate_reports(
    all: bool = typer.Option(None, "-a", "--all", help="Generates all reports"),
    year: int = typer.Option(None, "-y", "--year", help="Generates reports for this year"),
    month: int = typer.Option(None, "-m", "--month", help="In combination with year, limits report generation to this month"),
    current_month: bool = typer.Option(False, "-c", "--current-month", help="Generate report for the current month"),
    previous_month: bool = typer.Option(False, "-p", "--previous-month", help="Generate report for the previous month"),
):
    """
    Generate reports on CM for specified months and years with additional options for date range.
    """
    from src.downloads import generate_reports
    generate_reports(all, year, month, current_month, previous_month)

@app.command()
def summary(
    year: list[int] = typer.Option(
        None,
        "--year",
        "-y",
        help="Filter by year. Can be used multiple times: -y 2023 -y 2024",
    ),
    per_month: bool = typer.Option(
        False,
        "--per-month",
        "-m",
        help="Group results per month instead of per year",
    ),
    graph: bool = typer.Option(
        False,
        "--graph",
        "-g",
        help="Show graphical output"
    ),
):
    """
    A summary report of the downloaded purchase orders.
    """

    from src.search import summary

    year = year if year else []

    df = summary(year, per_month=per_month)

    if graph:
        from src.visualization import plot_summary
        print("\nGenerating plot...")
        plot_summary(df, per_month)


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        False,
        "-v",
        "--version",
        help="Show application version and exit",
        is_eager=True,
    )
):
    if version:
        print(APP_VERSION)
        exit(0)


if __name__ == "__main__":
    app()