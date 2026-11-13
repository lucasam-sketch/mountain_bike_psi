
from dataclasses import dataclass
from drafter import *


set_website_title("Mountain Bike Setup Calculator")
set_website_style("terminal")

set_site_information(
    author="Lucas Mercurio",
    description="A calculator for estimated mountain bike tire "
                "and suspension settings.",
    sources="Simplified pressure calculations created for "
            "this project.",
    planning="Project brainstorming and design worksheets "
             "are included in the repository.",
    links=[]
)

set_website_framed(False)


@dataclass
class Tire:
    """Stores information about one bike tire."""
    position: str
    width: float
    wheel_size: float
    tubeless: bool
    recommended_psi: float = 0.0


@dataclass
class State:
    """Stores all information about the rider and bike."""
    rider_weight: float
    bike_weight: float
    gear_weight: float
    fork_travel: int
    rear_travel: int
    terrain_type: str
    has_rear_suspension: bool
    tires: list[Tire]
    fork_pressure: float = 0.0
    rear_pressure: float = 0.0


def calculate_total_weight(rider_weight: float,
                           bike_weight: float,
                           gear_weight: float) -> float:
    """Calculates the combined rider, bike, and gear weight."""
    return rider_weight + bike_weight + gear_weight


def calculate_tire_pressure(tire: Tire,
                            total_weight: float,
                            terrain: str) -> float:
    """Calculates an estimated starting tire pressure."""

    pressure = total_weight / 8.5

    if tire.position == "front":
        pressure = pressure * 0.95
    else:
        pressure = pressure * 1.05

    if tire.width <= 2.3:
        pressure = pressure + 1
    elif tire.width >= 2.5:
        pressure = pressure - 1

    if tire.wheel_size <= 26:
        pressure = pressure + 1
    elif tire.wheel_size < 29:
        pressure = pressure + 0.5

    if tire.tubeless:
        pressure = pressure - 1.5

    if terrain == "Rocky":
        pressure = pressure + 1.5
    elif terrain == "Muddy":
        pressure = pressure - 1

    return round(pressure, 1)


def calculate_fork_pressure(rider_weight: float) -> float:
    """Estimates starting front fork pressure."""
    return rider_weight * 0.5


def calculate_rear_pressure(rider_weight: float) -> float:
    """Estimates starting rear shock pressure."""
    return rider_weight * 1.1


def calculate_target_sag(travel: float,
                         percentage: float) -> float:
    """Calculates target suspension sag in millimeters."""
    return travel * percentage / 100


@route
def index(state: State) -> Page:
    """Displays the home page and project introduction."""

    return Page(state, [
        Header("Mountain Bike Setup Calculator"),
        "Find estimated starting settings for your mountain bike.",
        " ",
        Header("How it works"),
        "1. Enter your rider and bike information.",
        "2. Enter your suspension information.",
        "3. Enter your tire information.",
        "4. View your recommended starting settings.",
        " ",
        "The calculator includes your riding gear in the total "
        "weight used for tire pressure calculations.",
        " ",
        Button("Start Setup", "bike_info_page")
    ])


@route
def bike_info_page(state: State) -> Page:
    """Collects rider, bike, and gear weight."""

    return Page(state, [
        Header("Rider and Bike Information"),
        "Enter your weights in pounds.",
        " ",
        "Rider weight:",
        TextBox("rider_weight", state.rider_weight),
        "Bike weight:",
        TextBox("bike_weight", state.bike_weight),
        "Gear weight:",
        TextBox("gear_weight", state.gear_weight),
        "Gear weight is usually around 10 pounds.",
        " ",
        Button("Save and Continue", "save_bike_info"),
        Button("Back Home", "index")
    ])


@route
def save_bike_info(state: State,
                   rider_weight: float,
                   bike_weight: float,
                   gear_weight: float) -> Page:
    """Saves the rider, bike, and gear weights."""

    state.rider_weight = rider_weight
    state.bike_weight = bike_weight
    state.gear_weight = gear_weight

    return suspension_page(state)


@route
def suspension_page(state: State) -> Page:
    """Collects suspension information."""

    return Page(state, [
        Header("Suspension Information"),
        "Enter your suspension travel in millimeters.",
        " ",
        "Front fork travel:",
        TextBox("fork_travel", state.fork_travel),
        "Does your bike have rear suspension?",
        CheckBox("has_rear_suspension",
                 state.has_rear_suspension),
        " ",
        "Rear suspension travel:",
        TextBox("rear_travel", state.rear_travel),
        "If your bike does not have rear suspension, "
        "the rear travel will be set to zero.",
        " ",
        Button("Save and Continue", "save_suspension"),
        Button("Back", "bike_info_page")
    ])


@route
def save_suspension(state: State,
                    fork_travel: int,
                    rear_travel: int,
                    has_rear_suspension: bool) -> Page:
    """Saves suspension information."""

    state.fork_travel = fork_travel
    state.has_rear_suspension = has_rear_suspension

    if has_rear_suspension:
        state.rear_travel = rear_travel
    else:
        state.rear_travel = 0
        state.rear_pressure = 0.0

    return tire_setup_page(state)


@route
def tire_setup_page(state: State) -> Page:
    """Collects information about both tires."""

    front_tire = state.tires[0]
    rear_tire = state.tires[1]

    return Page(state, [
        Header("Tire Information"),
        "Enter the information for each tire.",
        "Tire widths and wheel sizes should be in inches.",
        " ",
        Header("Front Tire"),
        "Front tire width:",
        TextBox("front_width", front_tire.width),
        "Front wheel size:",
        TextBox("front_wheel_size", front_tire.wheel_size),
        "Front tire is tubeless:",
        CheckBox("front_tubeless", front_tire.tubeless),
        " ",
        Header("Rear Tire"),
        "Rear tire width:",
        TextBox("rear_width", rear_tire.width),
        "Rear wheel size:",
        TextBox("rear_wheel_size", rear_tire.wheel_size),
        "Rear tire is tubeless:",
        CheckBox("rear_tubeless", rear_tire.tubeless),
        " ",
        Header("Riding Conditions"),
        "Choose the terrain you ride most often:",
        SelectBox(
            "terrain_type",
            ["Smooth", "Rocky", "Muddy", "Mixed"],
            state.terrain_type
        ),
        " ",
        Button("Save Tire Information", "save_tire_setup"),
        Button("Back", "suspension_page")
    ])


@route
def save_tire_setup(state: State,
                    front_width: float,
                    front_wheel_size: float,
                    front_tubeless: bool,
                    rear_width: float,
                    rear_wheel_size: float,
                    rear_tubeless: bool,
                    terrain_type: str) -> Page:
    """Saves tire information and riding conditions."""

    state.terrain_type = terrain_type

    front_tire = Tire(
        position="front",
        width=front_width,
        wheel_size=front_wheel_size,
        tubeless=front_tubeless
    )

    rear_tire = Tire(
        position="rear",
        width=rear_width,
        wheel_size=rear_wheel_size,
        tubeless=rear_tubeless
    )

    state.tires = [front_tire, rear_tire]

    return Page(state, [
        Header("Information Saved"),
        "Your bike information has been saved.",
        "You can now calculate your estimated setup.",
        " ",
        Button("Calculate My Setup", "calculate_setup"),
        Button("Edit Tire Information", "tire_setup_page")
    ])


@route
def calculate_setup(state: State) -> Page:
    """Calculates and updates the entire bike setup."""

    total_weight = calculate_total_weight(
        state.rider_weight,
        state.bike_weight,
        state.gear_weight
    )

    for tire in state.tires:
        tire.recommended_psi = calculate_tire_pressure(
            tire, total_weight, state.terrain_type
        )

    state.fork_pressure = calculate_fork_pressure(
        state.rider_weight
    )

    if state.has_rear_suspension:
        state.rear_pressure = calculate_rear_pressure(
            state.rider_weight
        )
    else:
        state.rear_pressure = 0.0

    return results_page(state)


@route
def results_page(state: State) -> Page:
    """Displays the calculated tire and suspension settings."""

    total_weight = calculate_total_weight(
        state.rider_weight,
        state.bike_weight,
        state.gear_weight
    )

    front_tire = state.tires[0]
    rear_tire = state.tires[1]

    front_sag = calculate_target_sag(
        state.fork_travel, 20
    )

    content = [
        Header("Your Mountain Bike Setup"),
        Header("Weight Information"),
        "Rider weight: " + str(state.rider_weight) + " lbs",
        "Bike weight: " + str(state.bike_weight) + " lbs",
        "Gear weight: " + str(state.gear_weight) + " lbs",
        "Total weight: " + str(total_weight) + " lbs",
        " ",
        Header("Tire Recommendations"),
        "Front tire: " + str(front_tire.recommended_psi) + " PSI",
        "Rear tire: " + str(rear_tire.recommended_psi) + " PSI",
        " ",
        "Front tire width: " + str(front_tire.width) + " inches",
        "Rear tire width: " + str(rear_tire.width) + " inches",
        "Terrain: " + state.terrain_type,
        " ",
        Header("Suspension Recommendations"),
        "Fork starting pressure: "
        + str(round(state.fork_pressure, 1)) + " PSI",
        "Target fork sag: 20%",
        "Target fork sag distance: "
        + str(round(front_sag, 1)) + " mm"
    ]

    if state.has_rear_suspension:
        rear_sag = calculate_target_sag(
            state.rear_travel, 30
        )

        content.extend([
            " ",
            "Rear shock starting pressure: "
            + str(round(state.rear_pressure, 1)) + " PSI",
            "Target rear sag: 30%",
            "Target rear sag distance: "
            + str(round(rear_sag, 1)) + " mm"
        ])
    else:
        content.append("This bike does not have rear suspension.")

    content.extend([
        " ",
        Header("Important"),
        "These are estimated starting settings, not exact "
        "manufacturer recommendations.",
        "Check your tire and suspension limits and measure "
        "your actual sag before riding.",
        " ",
        Button("Start Over", "index"),
        Button("Edit Bike Information", "bike_info_page")
    ])

    return Page(state, content)


# Tests

test_state = State(
    rider_weight=160.0,
    bike_weight=30.0,
    gear_weight=10.0,
    fork_travel=140,
    rear_travel=120,
    terrain_type="Rocky",
    has_rear_suspension=True,
    tires=[
        Tire("front", 2.4, 29, True),
        Tire("rear", 2.4, 29, True)
    ]
)

assert_equal(calculate_total_weight(160, 30, 10), 200)
assert_equal(calculate_fork_pressure(160), 80.0)
assert_equal(calculate_rear_pressure(160), 176.0)
assert_equal(calculate_target_sag(140, 20), 28.0)
assert_equal(calculate_target_sag(120, 30), 36.0)

assert_equal(
    calculate_tire_pressure(test_state.tires[0], 200, "Rocky"),
    22.4
)

assert_equal(
    calculate_tire_pressure(test_state.tires[1], 200, "Rocky"),
    24.7
)

assert_has(
    index(test_state),
    Button("Start Setup", "bike_info_page")
)

assert_has(
    bike_info_page(test_state),
    TextBox("rider_weight", 160.0)
)

assert_has(
    suspension_page(test_state),
    TextBox("fork_travel", 140)
)

assert_has(
    tire_setup_page(test_state),
    TextBox("front_width", 2.4)
)

assert_has(
    results_page(test_state),
    "Your Mountain Bike Setup"
)

bike_test = State(
    160.0, 30.0, 10.0, 140, 120, "Rocky", True,
    [Tire("front", 2.4, 29, True),
     Tire("rear", 2.4, 29, True)]
)

assert_equal(
    save_bike_info(bike_test, 170.0, 32.0, 12.0).state.rider_weight,
    170.0
)

suspension_test = State(
    160.0, 30.0, 10.0, 140, 120, "Rocky", True,
    [Tire("front", 2.4, 29, True),
     Tire("rear", 2.4, 29, True)]
)

assert_equal(
    save_suspension(suspension_test, 150, 130, True).state.rear_travel,
    130
)

tire_test = State(
    160.0, 30.0, 10.0, 140, 120, "Rocky", True,
    [Tire("front", 2.4, 29, True),
     Tire("rear", 2.4, 29, True)]
)

assert_equal(
    save_tire_setup(
        tire_test, 2.5, 29, True, 2.4, 29, True, "Mixed"
    ).state.terrain_type,
    "Mixed"
)

calculation_test = State(
    160.0, 30.0, 10.0, 140, 120, "Rocky", True,
    [Tire("front", 2.4, 29, True),
     Tire("rear", 2.4, 29, True)]
)

assert_equal(
    calculate_setup(calculation_test).state.fork_pressure,
    80.0
)


start_server(State(
    rider_weight=160.0,
    bike_weight=30.0,
    gear_weight=10.0,
    fork_travel=140,
    rear_travel=120,
    terrain_type="Rocky",
    has_rear_suspension=True,
    tires=[
        Tire("front", 2.4, 29, True),
        Tire("rear", 2.4, 29, True)
    ]
))
