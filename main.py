import os
import pandas as pd
import json

def load_data_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def save_data_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def set_character(data):
    print("Setting up Character:")
    for skill in data['player_levels']:
        while True:
            try:
                level = int(input(f"Enter the level for {skill}: "))
                if not 1 <= level <= 100:
                    raise ValueError("Level must be between 1 and 100.")
                data['player_levels'][skill] = level
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer between 1 and 100.")
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Setting up Character:")
    for skill in data['efficiencies']:
        while True:
            try:
                efficiency = int(input(f"Enter the efficiency (%) for {skill}: "))
                if not 0 <= efficiency <= 100:
                    raise ValueError("Efficiency must be between 0 and 100.")
                data['efficiencies'][skill] = efficiency
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer between 0 and 100.")

    save_data_to_json(data, 'data.json')
    print("Character set successfully.")

def suggest_best_skill_and_item(data, woodcutting_logs, mining_ores, fishes, smelting_bars):
    best_skill = None
    best_item = None
    max_income = 0

    for skill, items in {
        "Woodcutting": woodcutting_logs,
        "Mining": mining_ores,
        "Fishing": fishes,
        "Smelting": smelting_bars
    }.items():
        efficiency = data['efficiencies'][skill]
        player_level = data['player_levels'][skill]

        if player_level < 1:
            continue  # Skip if player level is less than 1

        for item, properties in items.items():
            if properties['level'] <= player_level:
                income = calculate_income(skill, efficiency, player_level, {item: properties})
                income = round(income, 2)  # Round income to 2 decimal places
                if income > max_income:
                    max_income = income
                    best_skill = skill
                    best_item = item

    return best_skill, best_item, max_income


def print_menu():
    print("Menu:")
    print("1. Set Character")
    print("2. Check Potential Income")
    print("3. Best Skill to Earn Gold")
    print("4. Quit")

def calculate_income(skill, efficiency, level, items):
    if skill == "Woodcutting":
        income = max(log["value"] * (3600 / max(1, round((log["base_time"] * (100 - efficiency)) / 100, 1))) for log in items.values() if log["level"] <= level)
        return income
    elif skill == "Mining":
        income = max(ore["value"] * (3600 / max(1, round((ore["base_time"] * (100 - efficiency)) / 100, 1))) for ore in items.values() if ore["level"] <= level)
        return income
    elif skill == "Fishing":
        income = max((fish["value"] - fish["bait_cost"]) * (3600 / max(1, round((fish["base_time"] * (100 - efficiency)) / 100, 1))) for fish in items.values() if fish["level"] <= level)
        return income
    elif skill == "Smelting":
        income = max(bar["gold_earned"] * (3600 / max(1, round((bar["base_time"] * (100 - efficiency)) / 100, 1))) for bar in items.values() if bar["level"] <= level)
        return income
    else:
        return 0  # Return 0 if skill is not recognized


def print_items_for_skill(skill, level, items):
    print(f"Available items for {skill} at level {level}:")
    for item, properties in items.items():
        if properties['level'] <= level:
            print(f"{item}: {properties}")
    print()

# Main program
data = load_data_from_json('data.json')
efficiencies = data['efficiencies']
woodcutting_logs = data['woodcutting_logs']
mining_ores = data['mining_ores']
fishes = data['fishes']
smelting_bars = data['smelting_bars']
player_levels = data['player_levels']

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print_menu()
    choice = input("Enter your choice (1-4): ")
    if choice == "4":
        print("Exiting...")
        break
    elif choice == "3":
        os.system('cls' if os.name == 'nt' else 'clear')
        best_skill, best_item, max_income = suggest_best_skill_and_item(data, woodcutting_logs, mining_ores, fishes, smelting_bars)
        print(f"Best skill to earn money: {best_skill}")
        print(f"Item to farm: {best_item}")
        print(f"Potential income: ${max_income:.2f}")  # Print income with 2 decimal places
        input("Press Enter to continue...")
    elif choice == "1":
        os.system('cls' if os.name == 'nt' else 'clear')
        set_character(data)
        input("Press Enter to continue...")
    elif choice == "2":
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Select a skill to check potential income:")
        print("1. Woodcutting")
        print("2. Mining")
        print("3. Fishing")
        print("4. Smelting")
        skill_choice = input("Enter your choice (1-4): ")
        if skill_choice in ["1", "2", "3", "4"]:
            os.system('cls' if os.name == 'nt' else 'clear')
            skill = {"1": "Woodcutting", "2": "Mining", "3": "Fishing", "4": "Smelting"}[skill_choice]
            efficiency = data['efficiencies'][skill]
            player_level = data['player_levels'][skill]  # Get the player's level for the chosen skill
            print(f"Potential income for {skill} at level {player_level}:")
            if skill == "Woodcutting":
                df = pd.DataFrame.from_dict(woodcutting_logs, orient='index')
                df = df[df['level'] <= player_level]  # Filter rows where level is less than or equal to player's level
                df.index.name = 'Log'
                df.columns = ['Level', 'Base Time', 'Value']  # Add 'Level' column here
                df['Time Efficiency'] = (df['Base Time'] / ((efficiency + 100) / 100)).round(1)
                df['Potential Income'] = (df['Value'] * (3600 / df['Time Efficiency'])).round(2)
            elif skill == "Mining":
                df = pd.DataFrame.from_dict(mining_ores, orient='index')
                df = df[df['level'] <= player_level]  # Filter rows where level is less than or equal to player's level
                df.index.name = 'Ore'
                df.columns = ['Level', 'Base Time', 'Value']  # Add 'Level' column here
                df['Time Efficiency'] = (df['Base Time'] / ((efficiency + 100) / 100)).round(1)
                df['Potential Income'] = (df['Value'] * (3600 / df['Time Efficiency'])).round(2)
            elif skill == "Fishing":
                df = pd.DataFrame.from_dict(fishes, orient='index')
                df = df[df['level'] <= player_level]  # Filter rows where level is less than or equal to player's level
                df.index.name = 'Fish'
                df.columns = ['Level', 'Base Time', 'Value', 'Bait Cost']  # Add 'Level' column here
                df['Time Efficiency'] = (df['Base Time'] / ((efficiency + 100) / 100)).round(1)
                df['Potential Income'] = ((df['Value'] - df['Bait Cost']) * (3600 / df['Time Efficiency'])).round(2)
            elif skill == "Smelting":
                df = pd.DataFrame.from_dict(smelting_bars, orient='index')
                df = df[df['level'] <= player_level]  # Filter rows where level is less than or equal to player's level
                df.index.name = 'Bar'
                df.columns = ['Level', 'Base Time', 'Gold Earned']  # Add 'Level' column here
                df['Time Efficiency'] = (df['Base Time'] / ((efficiency + 100) / 100)).round(1)
                df['Potential Income'] = ((df['Gold Earned'] * 3600) / df['Time Efficiency']).round(2)

                # Get the ore name (assuming it has the same name as the bar)
                ore_name = df.index[0]

                # Check if ore exists in the mining ores data
                if ore_name in mining_ores:
                    ore_time = round(mining_ores[ore_name]['base_time'] / ((efficiencies['Mining'] + 100) / 100), 1)
                    coal_time = round(mining_ores['Coal']['base_time'] / ((efficiencies['Mining'] + 100) / 100), 1)
                    total_time = ore_time + coal_time
                    df['Time Efficiency'] += total_time
                    df['Potential Income'] = ((df['Gold Earned'] * 3600) / df['Time Efficiency']).round(2)
                else:
                    print(f"No ore found for {ore_name}")

            # Print the DataFrame for inspection
        print(df)
        input("Press Enter to continue...")
    else:
        print("Invalid choice. Please enter a number from 1 to 4.")
        input("Press Enter to continue...")
