import typer
from typer.core import TyperGroup

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
    Downloads all reports that have been generated, doesn't download them again by cheching what has been downloaded. Specify year and month to redownload 1 report.
    """
    from downloads import download_reports
    download_reports(year, month)

from search import set_name_column, product_name_column, quantity_column, total_price_column, date_of_purchase_column
custom_columns = f"{set_name_column},{product_name_column},{quantity_column},{total_price_column},Price,{date_of_purchase_column}"
display_columns_help = f"Presets: Limited, Standard, Extended, Modern or Legacy. You can also customize what to show. Wrap the column names in \"quotations\". "
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
    display_columns: str = typer.Option(custom_columns, "-dc", "--display-columns", help=display_columns_help),
    limit: int = typer.Option(100, "-l", "--limit", help="Limit the number of rows displayed in the results.")
):
    """
    Search and format the order details with optional filtering, sorting, grouping, and summarization.
    """
    from search import search
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
    Generate reports for specified months and years with additional options for date range.
    """
    from downloads import generate_reports
    generate_reports(all, year, month, current_month, previous_month)

if __name__ == "__main__":
    app()