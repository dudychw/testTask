

### Инструкция для сборки и запуска:
Сборка и активация виртуального окружения:

```bash
sh build/build.sh
source venv/bin/activate
```

Local or background запуск:
```bash
python main.py
python main.py &
```

### Мониторинг состояния:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```
либо открыть в браузере по тем же запросам


---

## Description

### test.py  
Главный файл для запуска сервиса.  
Запускает:
- Подписку на пары через WebSocket Binance
- Сбор данных в очереди
- Получение и интерпретация метрик
- HTTP-сервер с эндпоинтами `/health` и `/metrics`. 

---

### ws_binance_api.py  
Отвечает за подписку на WebSocket Binance.  
Для каждой пары:
- Получает данные с помощью `.recv()`
- Сохраняет в `asyncio.Queue`
- Считает базовые метрики

---

### metrics_collector.py  
Читает из очередей и считает метрики:
- Общее число сообщений.
- Задержка события.
- Последняя цена.

---

### metrics_server.py  
HTTP-сервер (порт 8000) с двумя эндпоинтами:
- `/health` — возвращает OK/FAIL по свежести данных.
- `/metrics` — отображает текущие метрики.
---
## Tech Stack
Все протестировано локально на Fedora 42 с Python 3.12.10.

#### Ключевые библиотеки:
- binance
- binance-connector
- aiohttp

