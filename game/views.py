from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from game.models.state import State
from game.agents.agents import MinimaxABAgent, NegascoutAgent, CompetitiveAgent
import json
from queue import Queue
from .models.util import TimedFunction

def frontend(request):
    """
    Renderuje početnu HTML stranicu za igru.
    """
    return render(request, "index.html")

@csrf_exempt
def start_game(request):
    """
    Endpoint za pokretanje igre.
    Omogućava postavljanje startnog stanja i konfiguraciju igrača.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Preuzmi postavke iz zahteva
            player_red = data.get("player_red", "human")
            player_yellow = data.get("player_yellow", "human")
            max_depth = int(data.get("max_depth", 4))
            moves = data.get("moves", [])

            # Kreiraj početno stanje igre
            state = State()
            for move in moves:
                state = state.generate_successor_state(move)

            # Kreiraj agente
            agents = {
                "minimax": MinimaxABAgent(),
                "negascout": NegascoutAgent(),
                "competitive": CompetitiveAgent(),
                "human": None
            }
            red_agent = agents.get(player_red, None)
            yellow_agent = agents.get(player_yellow, None)

            # Proveri da li su agenti validni
            if red_agent is None and player_red != "human":
                return JsonResponse({"error": "Invalid agent for Red player."}, status=400)
            if yellow_agent is None and player_yellow != "human":
                return JsonResponse({"error": "Invalid agent for Yellow player."}, status=400)

            # Čuvaj podatke u sesiji
            request.session["state"] = state.to_dict()
            request.session["red_agent"] = player_red
            request.session["yellow_agent"] = player_yellow
            request.session["max_depth"] = max_depth

            return JsonResponse({"message": "Game started successfully!", "state": state.to_dict()}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def play_turn(request):
    """
    Endpoint za odigravanje poteza.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            column = data.get("column", None)

            # Preuzmi stanje iz sesije
            state_data = request.session.get("state")
            player_red = request.session.get("red_agent")
            player_yellow = request.session.get("yellow_agent")
            max_depth = request.session.get("max_depth", 4)

            # Rekonstruiši stanje
            state = State.from_dict(state_data)

            if state.get_state_status() is not None:
                return JsonResponse({"error": "Game is already finished."}, status=400)

            # Odigraj potez
            if column is None:
                current_agent = None
                if state.get_next_on_move() == State.RED:
                    current_agent = CompetitiveAgent() if player_red == "competitive" else None
                else:
                    current_agent = CompetitiveAgent() if player_yellow == "competitive" else None

                if current_agent:
                    column = current_agent.get_chosen_column(state, max_depth)

            if column is not None:
                state = state.generate_successor_state(column)

            # Ažuriraj stanje
            request.session["state"] = state.to_dict()

            # Proveri pobednika
            status = state.get_state_status()
            if status == State.RED:
                return JsonResponse({"message": "Red wins!", "state": state.to_dict()}, status=200)
            elif status == State.YEL:
                return JsonResponse({"message": "Yellow wins!", "state": state.to_dict()}, status=200)
            elif status == State.DRAW:
                return JsonResponse({"message": "Draw!", "state": state.to_dict()}, status=200)

            return JsonResponse({"message": "Move played.", "state": state.to_dict()}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

