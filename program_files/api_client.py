import requests
from datetime import datetime, timedelta
from datetime import datetime
import json
import customtkinter as ctk
import webbrowser

class MotivationAPI:
    @staticmethod
    def get_quote():
        try:
            response = requests.get("https://api.quotable.io/random", timeout=3)
            return response.json()["content"]
        except:
            return "Сосредоточьтесь и продолжайте учиться!"

class WorldTimeAPI:
    @staticmethod
    def get_formatted_time():
        try:
            response = requests.get("http://worldtimeapi.org/api/ip", timeout=3)
            data = response.json()
            dt = datetime.fromisoformat(data["datetime"])
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ScheduleAPI:
    BASE_URL = "https://ruz.spbstu.ru/api/v1/ruz"

    @staticmethod
    def get_group_info(group_id):
        try:
            response = requests.get(
                f"{ScheduleAPI.BASE_URL}/groups/{group_id}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            return {
                "name": data.get("name", "Неизвестно"),
                "faculty": data.get("faculty", {}).get("name", "Неизвестно"),
                "course": data.get("course", "Неизвестно")
            }
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения информации о группе: {e}")
            return {
                "name": "5130904/30101",
                "faculty": "Институт компьютерных наук и кибербезопасности",
                "course": 3
            }

    @staticmethod
    def get_group_schedule(group_id, date=None):
        try:
            # Если дата не указана, берем сегодня
            start_date = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d")

            # Структура для накопления данных
            combined_schedule = {
                "week": {
                    "date_start": start_date.strftime("%Y.%m.%d"),
                    "date_end": (start_date + timedelta(days=13)).strftime("%Y.%m.%d"),
                    "is_odd": False # Будет обновлено из первого успешного ответа
                },
                "days": []
            }

            # Запрашиваем данные на 2 недели (14 дней)
            for day_offset in range(14):
                current_date_obj = start_date + timedelta(days=day_offset)
                current_date_str = current_date_obj.strftime("%Y-%m-%d")

                try:
                    response = requests.get(
                        f"{ScheduleAPI.BASE_URL}/scheduler/{group_id}",
                        headers={"User-Agent": "Mozilla/5.0"},
                        params={"date": current_date_str},
                        timeout=5  # Уменьшил таймаут для ускорения цикла
                    )

                    if response.status_code == 200:
                        data = response.json()

                        # Обновляем инфо о неделе (is_odd) из первого успешного ответа
                        if combined_schedule["week"]["is_odd"] is False and data.get("week", {}).get("is_odd") is not None:
                            combined_schedule["week"]["is_odd"] = data["week"]["is_odd"]

                        # Если есть дни в ответе
                        if data.get("days"):
                            for day in data["days"]:
                                # Проверяем, что день совпадает с запрашиваемым (иногда API возвращает всю неделю)
                                if day.get("date") == current_date_str:
                                    # Обработка уроков (как раньше)
                                    processed_day = {
                                        "weekday": day.get("weekday"),
                                        "date": day.get("date"),
                                        "lessons": []
                                    }

                                    for lesson in day.get("lessons", []):
                                        # Формирование аудитории
                                        room = "Не указано"
                                        if lesson.get("auditories"):
                                            auds = lesson.get("auditories")
                                            if auds and len(auds) > 0:
                                                room = f"{auds[0].get('building', {}).get('name', '')} {auds[0].get('name', '')}".strip()

                                        # Формирование преподавателя
                                        teacher = "Не указан"
                                        if lesson.get("teachers"):
                                            teachers = lesson.get("teachers")
                                            if teachers and len(teachers) > 0:
                                                teacher = teachers[0].get("full_name", teacher)

                                        processed_day["lessons"].append({
                                            "time": f"{lesson.get('time_start', '')} - {lesson.get('time_end', '')}",
                                            "subject": lesson.get("subject", "Не указано"),
                                            "type": lesson.get("typeObj", {}).get("abbr", ""),
                                            "room": room,
                                            "teacher": teacher,
                                            "lms_url": lesson.get("lms_url", "")
                                        })

                                    combined_schedule["days"].append(processed_day)
                        else:
                            # Если дней нет, но запрос успешен (выходной), можно добавить пустой день для отображения
                            # Но логика main.py скорее всего просто пропустит отсутствующие дни
                            # Добавим пустую запись для календаря
                            combined_schedule["days"].append({
                                "weekday": current_date_obj.isoweekday(),
                                "date": current_date_str,
                                "lessons": []
                            })

                except Exception as e:
                    print(f"Ошибка загрузки дня {current_date_str}: {e}")
                    # Добавляем пустой день при ошибке
                    combined_schedule["days"].append({
                        "weekday": current_date_obj.isoweekday(),
                        "date": current_date_str,
                        "lessons": []
                    })

            return combined_schedule

        except Exception as e:
            print(f"Критическая ошибка получения расписания: {e}")
            # Возвращаем заглушку при полной неудаче
            return {
                "week": {
                    "is_odd": False,
                    "date_start": datetime.now().strftime("%Y.%m.%d"),
                    "date_end": (datetime.now() + timedelta(days=13)).strftime("%Y.%m.%d")
                },
                "days": []
            }
