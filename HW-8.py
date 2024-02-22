from datetime import datetime, timedelta
from collections import UserDict
import pickle, os

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        choice = input("Do you want to specify a different path? (y/n): ")
        if choice.lower() == 'y':
            new_filename = input("Enter the full path to the file, including the filename: ")
            return load_data(new_filename)  # Рекурсивно спробувати з новим шляхом
        else:
            print("Starting a new address book.")
            return AddressBook()
    elif not os.path.isfile(filename):
        print(f"The path {filename} is not a file. Please enter a valid file path, including the filename.")
        return AddressBook()
    else:
        with open(filename, "rb") as f:
            return pickle.load(f)

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits")
        self.value = value

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        if self.birthday is None:  
            self.birthday = Birthday(birthday)
        else:
            raise ValueError("Birthday is already set. To change it, use the change_birthday.")

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        raise ValueError("Old phone not found.")

    def show_phones(self):
        return ", ".join(phone.value for phone in self.phones)

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self):
        today = datetime.now()
        one_week_later = today + timedelta(days=7)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if today <= birthday_this_year <= one_week_later:
                    upcoming_birthdays.append((record.name.value, birthday_this_year.strftime("%d.%m.%Y")))
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)
    return inner

@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Please enter a name and at least one phone number.")
    name, phones = args[0], args[1:]
    record = book.data.get(name, Record(name))
    for phone in phones:
        record.add_phone(phone)
    book.add_record(record)
    return f"Contact {name} added/updated with phone(s): {'; '.join(phones)}."

@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise ValueError("Please enter a name, old phone number, and new phone number.")
    name, old_phone, new_phone = args
    if name not in book.data:
        raise KeyError("Contact not found.")
    book.data[name].change_phone(old_phone, new_phone)
    return f"Contact {name}'s phone number changed from {old_phone} to {new_phone}."

@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise ValueError("Please enter a name.")
    name = args[0]
    if name not in book.data:
        raise KeyError("Contact not found.")
    return f"{name}: {book.data[name].show_phones()}"

@input_error
def show_all(book):
    if not book.data:
        return "No contacts found."
    return "\n".join([f"{name}: {record.show_phones()}" for name, record in book.data.items()])

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Please enter a name and birthday in DD.MM.YYYY format.")
    name, birthday = args
    if name in book.data:
        book.data[name].add_birthday(birthday)
        return f"Birthday for {name} added."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise ValueError("Please enter a name.")
    name = args[0]
    if name in book.data and book.data[name].birthday:
        return f"{name}'s birthday is on {book.data[name].birthday.value.strftime('%d.%m.%Y')}"
    else:
        return "Birthday not found."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return "Upcoming birthdays:\n" + "\n".join([f"{name} on {date}" for name, date in upcoming])
    else:
        return "No upcoming birthdays next week."

def parse_input(user_input):
    parts = user_input.strip().split(' ', 2)
    command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    return command, args

def show_help():
    help_text = """
Available commands:
    hello - Greet the user.
    add [name] [phone...] - Add a new contact or update existing (multiple phones can be added).
    change [name] [old phone] [new phone] - Change the phone number of an existing contact.
    phone [name] - Show the phone number(s) of a contact.
    all - Show all saved contacts.
    add-birthday [name] [birthday] - Add or update a birthday for a contact.
    show-birthday [name] - Show the birthday of a contact.
    birthdays - List upcoming birthdays within the next week.
    help - Show available commands.
    close, exit - Exit the program.
    """
    print(help_text)

def main():
    book = load_data()  # Спроба завантажити існуючу адресну книгу
    print("Welcome to the assistant bot! Type 'help' to see all commands.")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)  # Зберегти стан адресної книги перед виходом
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(None, book))
        elif command == "help":
            show_help()
        else:
            print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()
