from dagster import op, job

@op
def get_name():
    """Simple op that returns a string."""
    return "Dagster"

@op
def greet(name: str):
    """Op that prints a greeting."""
    print(f"👋 Hello, {name}!")

@job
def hello_dagster_job():
    """A minimal job wiring get_name -> greet."""
    greet(get_name())