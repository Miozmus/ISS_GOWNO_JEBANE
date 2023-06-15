import Backend.HeatRegulator as hr
import Backend.ForceCalculator as fc
import numpy as np
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from plotly import graph_objs as go
import FuzzyRegulator as fg

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO], suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1(children='Regulacja wznoszenia balonu', style={
        'textAlign': 'center',
        'color': 'Green'
    }
            ),


    html.Br(),

    html.Label('Wybierz moc piecyka', style={'color': '#00ff00', 'textAlign': 'center'}),
    dcc.Slider(
        id='power_slider',
        min=1000,
        max=10000,
        value=3000,
        step=10,
        marks={i * 500: '{}'.format(i * 500) for i in range(20)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    html.Label('Wybierz czas trwania symulacji', style={'color': '#00ff00', 'textAlign': 'center'}),
    dcc.Slider(
        id='t_slider',
        min=100,
        max=500,
        value=200,
        step=10,
        marks={i * 100: '{}'.format(i * 100) for i in range(6)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    html.Div(children='Wybierz nastawy regulatora',
             style={
                 'color': '#ff0000',
                 'textAlign': 'center',
             }

             ),

    html.Label('Wybierz wartość współczynnika proporcjonalnego', style={'color': '#00ff00', 'textAlign': 'center'}),
    dcc.Slider(
        id='P_slider',
        min=0.0001,
        max=0.01,
        value=0.005,
        step=0.0001,
        marks={i*0.0005: '{}'.format(round(i*0.0005, 4)) for i in range(21)},
        tooltip={"placement": "bottom", "always_visible": True},
    ),
    html.Label('Wybierz wartość czasu zdwojenia', style={'color': '#00ff00', 'textAlign': 'center'}),
    dcc.Slider(
        id='I_slider',
        min=1,
        max=10000,
        value=3000,
        step=100,
        marks={i*500: '{}'.format(i*500) for i in range(22)},
        tooltip={"placement": "bottom", "always_visible": True}

    ),
    html.Label('Wybierz wartość czasu wyprzedzenia', style={'color': '#00ff00', 'textAlign': 'center'}),
    dcc.Slider(
        id='D_slider',
        min=1,
        max=50,
        value=25,
        step=0.001,
        marks={i*2: '{}'.format(i*2) for i in range(26)},
        tooltip={"placement": "bottom", "always_visible": True}

    ),

    html.Label('Wybierz wartość referencyjną wysokości:', style={'color': '#00ff00', 'textAlign': 'center'}),
    dcc.Input(id='href_input', value=1500, type='number'),

    html.Br(),
    html.Br(),

    dcc.Graph(id="v/t"),
    dcc.Graph(id="h/t"),
    dcc.Graph(id="e/t"),
    dcc.Graph(id="u_pi/t"),
    dcc.Graph(id="P_pid/t")

])


@app.callback(
    Output('v/t', 'figure'),
    Output('h/t', 'figure'),
    Output('e/t', 'figure'),
    Output('u_pi/t', 'figure'),
    Output('P_pid/t', 'figure'),
    Input('href_input', 'value'),
    Input('power_slider', 'value'),
    Input('t_slider', 'value'),
    Input('P_slider', 'value'),
    Input('I_slider', 'value'),
    Input('D_slider', 'value')
)
def update_values( selected_href, selected_power, selected_time, selected_P, selected_I, selected_D):
    # Parametry symulacji
    simTime = selected_time #500
    stepTime = 0.1
    t = [0]
    N = int(simTime / stepTime)

    # Parametry balonu
    mAir = 3.409  # masa powietrza wewnątrz balonu [kg]
    Vo = 5000  # objętość balonu [m^3]
    m = 900  # masa kosza [kg]
    Pmax = selected_power #3 * 1000  # moc piecyka [W]
    Pmin = 0
    Tdest = 390  # temperatura referencyjna [K]
    Tout = 293  # temperatura otoczenia [K]
    Tins = [Tout]  # temperatura wewnątrz balonu
    hTarget = selected_href #1500  # wysokość docelowa [m]

    # kontenery dla wartości
    F = [0]  # siła wyporności [N]
    h = [0]  # wysokość [m]
    Ve = [0]  # prędkość [m/s]
    currHeat = 0
    P_pid = [0] #moc chwilowa wyznaczona przez PID [W]
    P_fuzzy = [0]  #moc chwilowa ywznaczona przez regulator rozmyty [W]

    #parametry regulatora PID
    e = [hTarget - h[-1]] #uchyb
    epsilon = 0.01; #granica błędu regulacji
    kp = selected_P #1.5; #współczynnik wzmocnienia członu proporcjonalnego
    Ti = selected_I #10; #czas zdwojenia członu całkującego [s]
    Td = selected_D #10; #czas wyprzedzenia członu różniczującego [s]
    I=0.0; #
    u_pi=[0.0]; #sygnał wychodzący z regulatora
    umax=10; #sygnał sterujący [V]
    umin=-10;


    for n in range(1, N):
        t.append(t[-1] + stepTime)
        e.append(hTarget - h[-1])
        Prop = e[-1] * kp;
        I =  stepTime / Ti * (I + e[-1] * (t[-1] - t[-2]))
        D = Td / Ti * (e[-1] - e[-2]) / (t[-1] - t[-2])
        u_pi.append(np.clip(Prop + I + D, umin, umax))
        P_pid.append((Pmax - Pmin) / (umax - umin) * (u_pi[-1] - umin) + Pmin);
        #P_fuzzy.append(fg.Fuzzy_regulator(hTarget, Pmax, h[-1]))

        currHeat += P_pid[-1]*stepTime
        # myślę, że P powinniśmy regulować za pomocą regulatorów wtedy regulujemy temperaturę i dzięki temu pozostałe wielkości
        # 1W = 1J/1S -> Heat = Power * time

        if (Tins[-1] > Tdest): #ograniczenie dla temperatury wewnątrz balonu
            Tins[-1] = Tins[-2]
        else:
            Tins.append(Tins[-1] + hr.calculateAirTemperature(currHeat, mAir))

        Ftemp = fc.calculateForce(m, h[-1], Vo, Tout, Tins[-1], Ve[-1])
        if (Ftemp < 0 and h[-1] < 3):  # spełnienie tych warunków oznacza, że balon nie wystartował
            F.append(0)
        else:  # dzięki uwzględnieniu ujemnych mocy mamy od razu spadek swobodny
            F.append(Ftemp)
        #jeśli siła wyporności zmalała to prędkośc też maleje
        deltaF = F[-1] - F[-2]
        if (deltaF < 0):
            Ve.append(Ve[-1] - F[-1]/(mAir+m)*stepTime)
        else:
            Ve.append(Ve[-1] + F[-1]/(mAir+m)*stepTime)
        if(Ve[-1] > 30):
            Ve[-1] = Ve[-2]
        deltaVe = Ve[-1] - Ve[-2]
        # if (deltaVe < 0): #jeśli prędkość zmalała to wysokość też musi maleć
        #     h.append(Ve[-1] * t[-1])
        # else: #jeśli prędkość się zwiększyła wciąż lecimy do góry
        h.append(Ve[-1] * t[-1])
    # TODO
    #  ogarnąć falowanie wartości

    print('t:', t)
    print('Tins: ', Tins)
    print('F: ', F)
    print('Ve: ', Ve)
    print('h: ', h)
    print('e: ', e)
    print('u_pi: ', u_pi)
    print('P: ', Prop)
    print('I: ', I)
    print('D: ', D)
    print('P: ', P_pid)

    fig1 = {
        'data': [
            go.Scatter(
                x=t,
                y=Ve,
                mode='lines',
                line = dict(color='#ff0000')
            )
        ],

        'layout': go.Layout(
            title='wykres prędkości balonu w funkcji czasu',
            plot_bgcolor='white',

            xaxis={'title': 'czas[s]'},
            yaxis={'title': 'prędkość [m/s]'}
        )
    }

    fig2 = {
        'data': [
            go.Scatter(
                x=t,
                y=h,
                mode='lines',
                line=dict(color='#00ff00')
            )
        ],

        'layout': go.Layout(
            title='wykres wysokości balonu w funkcji czasu',
            plot_bgcolor='white',

            xaxis={'title': 'czas[s]'},
            yaxis={'title': 'wysokość [m]'}
        )
    }

    fig3 = {
        'data': [
            go.Scatter(
                x=t,
                y=e,
                mode='lines',
                line=dict(color='#a0a0ff')
            )
        ],

        'layout': go.Layout(
            title='wykres zmiany wartości uchybu w funkcji czasu',
            plot_bgcolor='white',

            xaxis={'title': 'czas[s]'},
            yaxis={'title': 'wartość uchybu'}
        )
    }

    fig4 = {
        'data': [
            go.Scatter(
                x=t,
                y=u_pi,
                mode='lines',
                line=dict(color='#ffff00')
            )
        ],

        'layout': go.Layout(
            title='sygnał sterujący u_pi w funkcji czasu',
            plot_bgcolor='white',

            xaxis={'title': 'czas[s]'},
            yaxis={'title': 'sygnał sterujący u_pi [V]'}
        )
    }

    fig5 = {
        'data': [
            go.Scatter(
                x=t,
                y=P_pid,
                mode='lines',
                line=dict(color='#ccab77')
            )
        ],

        'layout': go.Layout(
            title='wykres mocy piecyka w funkcji czasu',
            plot_bgcolor='white',

            xaxis={'title': 'czas[s]'},
            yaxis={'title': 'moc [W]'}
        )
    }

    return fig1, fig2, fig3, fig4, fig5


app.run_server(debug=True)