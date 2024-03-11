"""
Модуль бота-помічника
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Tuple

class Field:
    """Базовий клас для полів запису."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    """
    Клас для зберігання імені контакту. Обов'язкове поле.
    """
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    """
    Клас для зберігання номера телефону. Має валідацію формату (10 цифр).
    """
    def __init__(self, value):
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format. Must be a string of 10 digits.")
        super().__init__(value)

class Birthday(Field):
    """
    Клас для зберігання дати народження. Має валідацію формату (DD.MM.YYYY).
    """
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid birthday format. Must be in the format DD.MM.YYYY.")
        super().__init__(value)

class Record:
    """
    Клас для зберігання інформації про контакт, включаючи ім'я, список телефонів та дату народження.
    """
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        """
        Додавання телефону до запису.
        """
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        """
        Видалення телефону з запису.
        """
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_phone_number, new_phone_number):
        """
        Редагування номера телефону в запису.
        """
        for phone in self.phones:
            if phone.value == old_phone_number:
                phone.value = new_phone_number

    def add_birthday(self, birthday):
        """
        Додавання дня народження до запису.
        """
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(str(phone) for phone in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday}"

class AddressBook:
    """
    Клас для зберігання та управління записами.
    """
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        """
        Додавання запису.
        """
        self.data[record.name.value] = record

    def find(self, name):
        """
        Пошук запису за ім'ям.
        """
        return self.data.get(name)

    def delete(self, name):
        """
        Видалення запису за ім'ям.
        """
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        """
        Повертає список контактів, яких потрібно привітати протягом наступного тижня.
        """
        birthdays_by_day = defaultdict(list)
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, '%d.%m.%Y').date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days

                if delta_days < 7:
                    birthday_day = (today + timedelta(days=delta_days)).strftime("%A")
                    if birthday_day == "Saturday" or birthday_day == "Sunday":
                        birthday_day = "Monday"
                    birthdays_by_day[birthday_day].append(record.name.value)

        return birthdays_by_day

def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """
    Розбирає введений користувачем рядок та виділяє команду та аргументи.

    Параметри:
    - user_input (str): Рядок введення від користувача.

    Повертає:
    - tuple: Кортеж, що містить команду (str) та аргументи (list).
    """
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args
def input_error(func):
    """
    Декоратор для обробки помилок у функціях.

    Parameters:
    - func: Функція, яку обгортати декоратором.

    Returns:
    - inner: Обгорнута функція з обробкою помилок.
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments provided."

    return inner

@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    """
    Додає новий контакт до адресної книги.

    Параметри:
    - args (list): Список, що містить ім'я та номер телефону.
    - book (AddressBook): Екземпляр класу AddressBook, де зберігаються контакти.

    Повертає:
    - str: Повідомлення про успішне додавання контакту.
    """
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

@input_error
def change_contact(args: List[str], book: AddressBook) -> str:
    """
    Змінює номер телефону для існуючого контакту.

    Параметри:
    - args (list): Список, що містить ім'я та новий номер телефону.
    - book (AddressBook): Екземпляр класу AddressBook, де зберігаються контакти.

    Повертає:
    - str: Повідомлення про успішну зміну контакту або про помилку, якщо ім'я не знайдено.
    """
    name, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, new_phone)
        return "Contact updated."
    else:
        return f"Contact {name} not found."

@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    """
    Виводить номер телефону для зазначеного контакту.

    Параметри:
    - args (list): Список, що містить ім'я контакту.
    - book (AddressBook): Екземпляр класу AddressBook, де зберігаються контакти.

    Повертає:
    - str: Номер телефону для вказаного контакту або повідомлення про помилку, 
    якщо ім'я не знайдено.
    """
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s phone number: {record.phones[0]}"
    else:
        return f"Contact {name} not found."

@input_error
def show_all(book: AddressBook) -> str:
    """
    Виводить усі збережені контакти.

    Параметри:
    - book (AddressBook): Екземпляр класу AddressBook, де зберігаються контакти.

    Повертає:
    - str: Рядок із всіма збереженими контактами та їхніми номерами телефонів або повідомлення про їх відсутність.
    """
    if book.data:
        result = "All contacts:\n"
        for record in book.data.values():
            result += f"{record}\n"
        return result.strip()
    else:
        return "No contacts found."
@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    """
    Додає день народження до контакту.

    Параметри:
    - args (list): Список, що містить ім'я та день народження (DD.MM.YYYY).
    - book (AddressBook): Екземпляр класу AddressBook, де зберігаються контакти.

    Повертає:
    - str: Повідомлення про успішне додавання дня народження або про помилку, якщо ім'я не знайдено.
    """
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return f"Contact {name} not found."

@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    """
    Виводить день народження для зазначеного контакту.
    """
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday}"
    elif record:
        return f"{name} has no birthday specified."
    else:
        return f"Contact {name} not found."

@input_error
def show_birthdays(book: AddressBook) -> str:
    """
    Показує контакти, яких потрібно привітати по днях на наступному тижні.
    """
    birthdays_per_week = book.get_birthdays_per_week()

    if birthdays_per_week:
        result = "Birthdays for the next week:\n"
        for day, names in birthdays_per_week.items():
            result += f"{day}: {', '.join(names)}\n"
        return result.strip()
    else:
        return "No birthdays in the next week."

def main():
    """
    Основна функція для взаємодії з користувачем у консольному режимі.
    """
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
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
            print(show_birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()