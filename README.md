# Tarea 3 de Redes

```bash
python3 -OO fragmentizador.py localhost:55550 localhost:55551:100 localhost:55552:200
python3 -OO fragmentizador.py localhost:55551 localhost:55552:200 localhost:55554:400
python3 -OO fragmentizador.py localhost:55552 localhost:55553:300
python3 -OO fragmentizador.py localhost:55553 localhost:55554:400
python3 -OO fragmentizador.py localhost:55554
```
