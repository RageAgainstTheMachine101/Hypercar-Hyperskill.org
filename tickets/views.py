from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render


# constants
CHANGE_OIL = 'change_oil'
INFLATE_TIRES = 'inflate_tires'
DIAGNOSTIC = 'diagnostic'
CHANGE_OIL_MINUTES = 2
INFLATE_TIRES_MINUTES = 5
DIAGNOSTICS_MINUTES = 30
SERVICES = {CHANGE_OIL: CHANGE_OIL_MINUTES, INFLATE_TIRES: INFLATE_TIRES_MINUTES,
            DIAGNOSTIC: DIAGNOSTICS_MINUTES}

ticket_n = 0
clients = {'change_oil': [], 'inflate_tires': [], 'diagnostic': []}
tickets_and_minutes = dict()
current_client = None


def get_ticket_and_minutes_to_wait(data: dict) -> dict:
    minutes_to_wait = 0
    queue = dict()

    for service, duration in SERVICES.items():
        for ticket in data.get(service):
            queue[ticket] = minutes_to_wait
            minutes_to_wait += duration

    return queue


class WelcomeView(View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


class MenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'menu.html', context={})


class TicketView(View):
    def get(self, request, *args, **kwargs):
        global ticket_n, clients, tickets_and_minutes

        service = request.path.split('/')[-2]
        ticket_n += 1
        clients[service].append(ticket_n)
        tickets_and_minutes = get_ticket_and_minutes_to_wait(clients)
        minutes_to_wait = tickets_and_minutes[ticket_n]

        return render(request, 'tickets.html', context={'ticket_n': ticket_n,
                                                        'minutes_to_wait': minutes_to_wait})


class ProcessingView(View):
    global clients

    def get(self, request, *args, **kwargs):
        return render(request, 'processing.html', context={'clients': clients})

    def post(self, request):
        global tickets_and_minutes, current_client

        if tickets_and_minutes:
            current_client = min(tickets_and_minutes, key=tickets_and_minutes.get)
        else:
            current_client = None

        for service in clients:
            if current_client in clients[service]:
                clients[service].pop(0)
                tickets_and_minutes = get_ticket_and_minutes_to_wait(clients)

        return render(request, 'processing.html', context={'clients': clients})


class NextClientView(View):
    def get(self, request, *args, **kwargs):
        global current_client

        return render(request, 'next_client.html', context={'current_client': current_client})
