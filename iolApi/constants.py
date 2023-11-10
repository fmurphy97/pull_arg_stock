URL_TOKEN = 'https://api.invertironline.com/token'
GRANT_TYPE = 'password'
URL_API = 'https://api.invertironline.com/api/v2/'

COUNTRIES = ['argentina', 'estados_Unidos']
MARKETS = ['bcBA', 'nYSE', 'nASDAQ', 'aMEX', 'bCS', 'rOFX']
PERIODS = ["t0", "t1", "t2"]
INSTRUMENT_TYPES = ['acciones', 'opciones', 'monedas', 'cedears', 'titulosPublicos', 'cauciones', 'cHPD', 'futuros',
                    'aDRs', 'obligacionesNegociables', 'letras']
INSTRUMENT_TYPES_FOR_PANEL = {
    'bonos': ['todos', 'soberanosEnPesosMasCer', 'soberanosEnPesosTasaVariable', 'soberanosEnPesosTasaFija',
              'soberanosEnDolares', 'soberanosDolarLinked', 'provincialesEnPesos', 'provincialesDolarLinked',
              'provincialesEnDolares', 'provincialesEnEuros', 'CuponesVinculadosAlPbi', 'letrasEnPesos',
              'letrasEnDolares'],
    'acciones': ['lideres', 'general', 'subastas'],
    'opciones': ['todas', 'deAcciones', 'deBonos', 'deCedears', 'inTheMoney', 'outOfTheMoney', 'calls', 'puts'],
    'monedas': ['todas'],
    'cauciones': ['todas'],
    'cHPD': [],
    'futuros': [],
    'aDRs': [],
    'obligacionesNegociables': ['todos'],
    'letras': ['todas', 'letrasDeDescuento', 'letrasCapitalizables', 'letrasVariable']
}

STATE = ['todas', 'pendientes', 'terminadas', 'canceladas']
