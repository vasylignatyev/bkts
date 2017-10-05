#!/usr/bin/python3

### DATA

data = {}

# Data on statusbar
data['statusbar'] = dict(driver='Петренко М.С.', route='A18', delay=-1)

# Pane tab data
tab_data = {}

# bort tab:
tab_data['bort'] = ""

# stop tab: STOP-NAME  SCHEDULE-TIME  LEAD-LAG
tab_data['stop'] = [
    dict(name="ст. м. Харківська",   schedule=8,  lag=1),
    dict(name="Ринок (на вимогу)",   schedule=9,  lag=-1),
    dict(name="вул. Кошиця",         schedule=11, lag=0),
    dict(name="вул. Олійника",       schedule=13, lag=1),
    dict(name="вул. Тростянецька",   schedule=0,  lag=-1000),   # < GREY_LAG
    dict(name="Магазин (на вимогу)", schedule=3,  lag=0),
    dict(name="вул. Російська",      schedule=4,  lag=-1000),
    dict(name="вул. Новодарницька",  schedule=6,  lag=-1000),
    dict(name="ш. Харківське",       schedule=7,  lag=-1000),
]

tab_data['stop'] = [
    dict(name="ст. м. Харківська",   schedule=8,  lag=1),
    dict(name="Ринок (на вимогу)",   schedule=9,  lag=-1),
    dict(name="вул. Кошиця",         schedule=11, lag=0),
    dict(name="вул. Олійника",       schedule=13, lag=1),
    dict(name="вул. Тростянецька",   schedule=0,  lag=-1000),   # < GREY_LAG
    dict(name="Магазин (на вимогу)", schedule=3,  lag=0),
    dict(name="вул. Російська",      schedule=4,  lag=-1000),
    dict(name="вул. Новодарницька",  schedule=6,  lag=-1000),
    dict(name="ш. Харківське",       schedule=7,  lag=-1000),
]


# route tab: some descriptive table
tab_data['route'] = [
    dict(item="Початок",       desc="ст. м. Харківська"),
    dict(item="Кінець",        desc="ш. Харківське"),
    dict(item="Вартість",      desc="4.0 грн"),
    dict(item="Відстань",      desc="4.32 км"),
    dict(item="Інтервал",      desc="6-13 хв"),
    dict(item="Робочі дні",    desc="Пн Вт Ср Чт Пт Сб Нд"),
    dict(item="Робочі години", desc="06:00 - 23:39"),
    dict(item="Компанія",      desc='КП “Київпастранс”'),
    dict(item="Телефон",       desc="(044) 528-30-11"),
    dict(item="Оновлення",     desc="06/08/2017")
]

# map tab: a bus moving (for example)
tab_data['map'] = [
	[50.400812, 30.651314],
	[50.400812, 30.651314],
	[50.400835, 30.651481],
	[50.400858, 30.651648],
	[50.400881, 30.651815],
	[50.400905, 30.651983],
	[50.400928, 30.652150],
	[50.400951, 30.652317],
	[50.400989, 30.652507],
	[50.401026, 30.652696],
	[50.401064, 30.652886],
	[50.401102, 30.653075],
	[50.401139, 30.653264],
	[50.401177, 30.653454],
	[50.401127, 30.653520],
	[50.401077, 30.653586],
	[50.401027, 30.653652],
	[50.400976, 30.653719],
	[50.400926, 30.653785],
	[50.400876, 30.653851],
	[50.400747, 30.653708],
	[50.400618, 30.653565],
	[50.400489, 30.653422],
	[50.400361, 30.653279],
	[50.400232, 30.653136],
	[50.400103, 30.652993],
	[50.400103, 30.652993],
	[50.400103, 30.652993],
	[50.400183, 30.652873],
	[50.400263, 30.652753],
	[50.400343, 30.652634],
	[50.400422, 30.652514],
	[50.400502, 30.652394],
	[50.400582, 30.652274],
	[50.400666, 30.652235],
	[50.400751, 30.652195],
	[50.400835, 30.652156],
	[50.400919, 30.652117],
	[50.401004, 30.652077],
	[50.401088, 30.652038],
	[50.401179, 30.652011],
	[50.401270, 30.651984],
	[50.401362, 30.651958],
	[50.401453, 30.651931],
	[50.401544, 30.651904],
	[50.401635, 30.651877],
	[50.401740, 30.651840],
	[50.401845, 30.651804],
	[50.401950, 30.651767],
	[50.402056, 30.651730],
	[50.402161, 30.651694],
	[50.402266, 30.651657],
	[50.402266, 30.651657],
	[50.402266, 30.651657],
	[50.402360, 30.651622],
	[50.402455, 30.651587],
	[50.402549, 30.651553],
	[50.402643, 30.651518],
	[50.402738, 30.651483],
	[50.402832, 30.651448],
	[50.402923, 30.651409],
	[50.403014, 30.651369],
	[50.403105, 30.651330],
	[50.403197, 30.651291],
	[50.403288, 30.651251],
	[50.403379, 30.651212],
	[50.403512, 30.651183],
	[50.403646, 30.651155],
	[50.403779, 30.651126],
	[50.403912, 30.651097],
	[50.404046, 30.651069],
	[50.404179, 30.651040],
	[50.404301, 30.650983],
	[50.404423, 30.650926],
	[50.404545, 30.650869],
	[50.404667, 30.650811],
	[50.404789, 30.650754],
	[50.404911, 30.650697],
	[50.405004, 30.650641],
	[50.405098, 30.650586],
	[50.405192, 30.650531],
	[50.405285, 30.650475],
	[50.405379, 30.650419],
	[50.405472, 30.650364],
	[50.405559, 30.650314],
	[50.405645, 30.650264],
	[50.405732, 30.650214],
	[50.405818, 30.650164],
	[50.405904, 30.650114],
	[50.405991, 30.650064],
	[50.406053, 30.650046],
	[50.406115, 30.650027],
	[50.406177, 30.650009],
	[50.406240, 30.649991],
	[50.406302, 30.649972],
	[50.406364, 30.649954],
	[50.406364, 30.649954],
	[50.406364, 30.649954],
	[50.406464, 30.649874],
	[50.406563, 30.649794],
	[50.406663, 30.649714],
	[50.406763, 30.649633],
	[50.406862, 30.649553],
	[50.406962, 30.649473],
	[50.407038, 30.649427],
	[50.407115, 30.649380],
	[50.407191, 30.649334],
	[50.407267, 30.649287],
	[50.407344, 30.649241],
	[50.407420, 30.649194],
	[50.407511, 30.649139],
	[50.407602, 30.649083],
	[50.407694, 30.649028],
	[50.407785, 30.648973],
	[50.407876, 30.648917],
	[50.407967, 30.648862],
	[50.408047, 30.648810],
	[50.408127, 30.648758],
	[50.408206, 30.648707],
	[50.408286, 30.648655],
	[50.408366, 30.648603],
	[50.408446, 30.648551],
	[50.408538, 30.648497],
	[50.408631, 30.648444],
	[50.408723, 30.648390],
	[50.408815, 30.648336],
	[50.408908, 30.648283],
	[50.409000, 30.648229],
	[50.409098, 30.648168],
	[50.409196, 30.648107],
	[50.409294, 30.648046],
	[50.409392, 30.647986],
	[50.409490, 30.647925],
	[50.409588, 30.647864],
	[50.409667, 30.647816],
	[50.409745, 30.647767],
	[50.409824, 30.647719],
	[50.409903, 30.647671],
	[50.409981, 30.647622],
	[50.410060, 30.647574],
	[50.410127, 30.647555],
	[50.410194, 30.647536],
	[50.410260, 30.647517],
	[50.410327, 30.647499],
	[50.410394, 30.647480],
	[50.410461, 30.647461],
	[50.410461, 30.647461],
	[50.410461, 30.647461],
	[50.410589, 30.647371],
	[50.410717, 30.647281],
	[50.410845, 30.647191],
	[50.410973, 30.647100],
	[50.411101, 30.647010],
	[50.411229, 30.646920],
	[50.411354, 30.646843],
	[50.411480, 30.646766],
	[50.411605, 30.646690],
	[50.411730, 30.646613],
	[50.411856, 30.646536],
	[50.411981, 30.646459],
	[50.412117, 30.646384],
	[50.412252, 30.646309],
	[50.412388, 30.646234],
	[50.412524, 30.646158],
	[50.412659, 30.646083],
	[50.412795, 30.646008],
	[50.412851, 30.646026],
	[50.412907, 30.646044],
	[50.412963, 30.646062],
	[50.413018, 30.646079],
	[50.413074, 30.646097],
	[50.413130, 30.646115],
	[50.413170, 30.646097],
	[50.413210, 30.646079],
	[50.413250, 30.646062],
	[50.413289, 30.646044],
	[50.413329, 30.646026],
	[50.413369, 30.646008],
	[50.413396, 30.645926],
	[50.413424, 30.645844],
	[50.413451, 30.645761],
	[50.413478, 30.645679],
	[50.413506, 30.645597],
	[50.413533, 30.645515],
	[50.413581, 30.645484],
	[50.413629, 30.645454],
	[50.413677, 30.645423],
	[50.413724, 30.645393],
	[50.413772, 30.645363],
	[50.413820, 30.645332],
	[50.413932, 30.645260],
	[50.414043, 30.645189],
	[50.414155, 30.645117],
	[50.414267, 30.645046],
	[50.414378, 30.644975],
	[50.414490, 30.644903],
	[50.414490, 30.644903],
	[50.414490, 30.644903],
	[50.414482, 30.644910],
	[50.414474, 30.644917],
	[50.414466, 30.644925],
	[50.414458, 30.644932],
	[50.414450, 30.644939],
	[50.414442, 30.644946],
	[50.414567, 30.644866],
	[50.414693, 30.644785],
	[50.414818, 30.644704],
	[50.414943, 30.644624],
	[50.415069, 30.644543],
	[50.415194, 30.644463],
	[50.415306, 30.644399],
	[50.415417, 30.644334],
	[50.415529, 30.644270],
	[50.415641, 30.644206],
	[50.415752, 30.644141],
	[50.415864, 30.644077],
	[50.415956, 30.644054],
	[50.416048, 30.644032],
	[50.416140, 30.644009],
	[50.416232, 30.643987],
	[50.416324, 30.643964],
	[50.416416, 30.643942],
	[50.416416, 30.643942],
	[50.416416, 30.643942],
	[50.416496, 30.643868],
	[50.416576, 30.643794],
	[50.416657, 30.643719],
	[50.416737, 30.643645],
	[50.416817, 30.643571],
	[50.416897, 30.643497],
	[50.416993, 30.643438],
	[50.417088, 30.643379],
	[50.417184, 30.643320],
	[50.417280, 30.643261],
	[50.417375, 30.643202],
	[50.417471, 30.643143],
	[50.417602, 30.643064],
	[50.417733, 30.642986],
	[50.417864, 30.642907],
	[50.417995, 30.642828],
	[50.418126, 30.642750],
	[50.418257, 30.642671],
	[50.418365, 30.642605],
	[50.418473, 30.642539],
	[50.418582, 30.642473],
	[50.418690, 30.642406],
	[50.418798, 30.642340],
	[50.418906, 30.642274],
	[50.419004, 30.642217],
	[50.419102, 30.642160],
	[50.419200, 30.642103],
	[50.419298, 30.642045],
	[50.419396, 30.641988],
	[50.419494, 30.641931],
	[50.419563, 30.641919],
	[50.419632, 30.641908],
	[50.419702, 30.641896],
	[50.419771, 30.641884],
	[50.419840, 30.641873],
	[50.419909, 30.641861],
	[50.419909, 30.641861],
	[50.419909, 30.641861],
	[50.419995, 30.641774],
	[50.420081, 30.641688],
	[50.420166, 30.641601],
	[50.420252, 30.641514],
	[50.420338, 30.641428],
	[50.420424, 30.641341],
	[50.420525, 30.641228],
	[50.420627, 30.641116],
	[50.420728, 30.641003],
	[50.420829, 30.640890],
	[50.420931, 30.640778],
	[50.421032, 30.640665],
	[50.421145, 30.640599],
	[50.421258, 30.640533],
	[50.421370, 30.640466],
	[50.421483, 30.640400],
	[50.421596, 30.640334],
	[50.421709, 30.640268],
	[50.421823, 30.640196],
	[50.421937, 30.640125],
	[50.422051, 30.640054],
	[50.422165, 30.639982],
	[50.422279, 30.639910],
	[50.422393, 30.639839],
	[50.422522, 30.639757],
	[50.422650, 30.639674],
	[50.422779, 30.639592],
	[50.422908, 30.639510],
	[50.423036, 30.639427],
	[50.423165, 30.639345],
	[50.423302, 30.639257],
	[50.423438, 30.639170],
	[50.423575, 30.639083],
	[50.423712, 30.638995],
	[50.423848, 30.638907],
	[50.423985, 30.638820],
	[50.424092, 30.638807],
	[50.424200, 30.638795],
	[50.424307, 30.638782],
	[50.424414, 30.638770],
	[50.424522, 30.638758],
	[50.424629, 30.638745],
	[50.424738, 30.638831],
	[50.424847, 30.638917],
	[50.424957, 30.639003],
	[50.425066, 30.639088],
	[50.425175, 30.639174],
	[50.425284, 30.639260],
	[50.425364, 30.639340],
	[50.425444, 30.639421],
	[50.425523, 30.639501],
	[50.425603, 30.639581],
	[50.425683, 30.639662],
	[50.425763, 30.639742],
	[50.425708, 30.639928],
	[50.425653, 30.640114],
	[50.425599, 30.640300],
	[50.425544, 30.640486],
	[50.425489, 30.640672],
	[50.425434, 30.640858],
	[50.425375, 30.641062],
	[50.425316, 30.641266],
	[50.425257, 30.641469],
	[50.425197, 30.641673],
	[50.425138, 30.641877],
	[50.425079, 30.642081],
	[50.425021, 30.642264],
	[50.424963, 30.642446],
	[50.424904, 30.642629],
	[50.424846, 30.642811],
	[50.424788, 30.642993],
	[50.424730, 30.643176],
	[50.424668, 30.643329],
	[50.424606, 30.643481],
	[50.424544, 30.643634],
	[50.424483, 30.643787],
	[50.424421, 30.643939],
	[50.424359, 30.644092],
	[50.424359, 30.644092],
	[50.424359, 30.644092],
	[50.424312, 30.644292],
	[50.424264, 30.644491],
	[50.424216, 30.644690],
	[50.424169, 30.644890],
	[50.424121, 30.645089],
	[50.424074, 30.645289],
	[50.424022, 30.645452],
	[50.423969, 30.645615],
	[50.423917, 30.645778],
	[50.423865, 30.645940],
	[50.423812, 30.646103],
	[50.423760, 30.646266],
	[50.423712, 30.646228],
	[50.423664, 30.646191],
	[50.423617, 30.646153],
	[50.423569, 30.646115],
	[50.423521, 30.646078],
	[50.423473, 30.646040],
	[50.423401, 30.645715],
	[50.423329, 30.645389],
	[50.423258, 30.645064],
	[50.423186, 30.644739],
	[50.423114, 30.644413],
	[50.423042, 30.644088],
	[50.423042, 30.644088],
	[50.423042, 30.644088],
	[50.423042, 30.644088],
	[50.423042, 30.644088],
	[50.423046, 30.643970],
	[50.423051, 30.643851],
	[50.423056, 30.643732],
	[50.423060, 30.643614],
	[50.423064, 30.643496],
	[50.423069, 30.643377],
	[50.423003, 30.643285],
	[50.422937, 30.643192],
	[50.422871, 30.643099],
	[50.422805, 30.643007],
	[50.422739, 30.642914],
	[50.422673, 30.642822],
	[50.422615, 30.642581],
	[50.422557, 30.642339],
	[50.422499, 30.642097],
	[50.422440, 30.641856],
	[50.422382, 30.641615],
	[50.422324, 30.641373],
	[50.422324, 30.641337],
	[50.422324, 30.641302],
	[50.422324, 30.641266],
	[50.422324, 30.641230],
	[50.422324, 30.641195],
	[50.422324, 30.641159],
	[50.422272, 30.640973],
	[50.422219, 30.640787],
	[50.422167, 30.640601],
	[50.422115, 30.640415],
	[50.422062, 30.640229],
	[50.422010, 30.640043],
	[50.421943, 30.640071],
	[50.421876, 30.640100],
	[50.421808, 30.640128],
	[50.421741, 30.640157],
	[50.421674, 30.640186],
	[50.421607, 30.640214],
	[50.421517, 30.640268],
	[50.421427, 30.640321],
	[50.421337, 30.640375],
	[50.421247, 30.640429],
	[50.421157, 30.640482],
	[50.421067, 30.640536],
	[50.420941, 30.640604],
	[50.420814, 30.640672],
	[50.420687, 30.640740],
	[50.420561, 30.640808],
	[50.420434, 30.640876],
	[50.420308, 30.640944],
	[50.420236, 30.640986],
	[50.420165, 30.641029],
	[50.420093, 30.641071],
	[50.420021, 30.641113],
	[50.419950, 30.641156],
	[50.419878, 30.641198],
	[50.419878, 30.641198],
	[50.419878, 30.641198],
	[50.419746, 30.641281],
	[50.419613, 30.641364],
	[50.419481, 30.641447],
	[50.419349, 30.641529],
	[50.419216, 30.641612],
	[50.419084, 30.641695],
	[50.418955, 30.641779],
	[50.418827, 30.641863],
	[50.418698, 30.641947],
	[50.418569, 30.642031],
	[50.418441, 30.642115],
	[50.418312, 30.642199],
	[50.418232, 30.642242],
	[50.418152, 30.642285],
	[50.418073, 30.642328],
	[50.417993, 30.642371],
	[50.417913, 30.642414],
	[50.417833, 30.642457],
	[50.417770, 30.642460],
	[50.417708, 30.642464],
	[50.417645, 30.642468],
	[50.417582, 30.642471],
	[50.417520, 30.642474],
	[50.417457, 30.642478],
	[50.417370, 30.642521],
	[50.417284, 30.642564],
	[50.417198, 30.642607],
	[50.417111, 30.642650],
	[50.417025, 30.642693],
	[50.416938, 30.642736],
	[50.416885, 30.642798],
	[50.416832, 30.642861],
	[50.416780, 30.642924],
	[50.416727, 30.642986],
	[50.416674, 30.643048],
	[50.416621, 30.643111],
	[50.416492, 30.643143],
	[50.416363, 30.643175],
	[50.416235, 30.643206],
	[50.416106, 30.643238],
	[50.415977, 30.643270],
	[50.415848, 30.643302],
	[50.415848, 30.643302],
	[50.415848, 30.643302],
	[50.415760, 30.643360],
	[50.415671, 30.643417],
	[50.415582, 30.643475],
	[50.415494, 30.643533],
	[50.415405, 30.643590],
	[50.415317, 30.643648],
	[50.415185, 30.643721],
	[50.415053, 30.643795],
	[50.414921, 30.643868],
	[50.414788, 30.643941],
	[50.414656, 30.644015],
	[50.414524, 30.644088],
	[50.414406, 30.644161],
	[50.414287, 30.644234],
	[50.414169, 30.644308],
	[50.414050, 30.644381],
	[50.413931, 30.644454],
	[50.413813, 30.644527],
	[50.413731, 30.644565],
	[50.413649, 30.644602],
	[50.413567, 30.644640],
	[50.413485, 30.644678],
	[50.413403, 30.644715],
	[50.413321, 30.644753],
	[50.413249, 30.644744],
	[50.413177, 30.644735],
	[50.413106, 30.644726],
	[50.413034, 30.644717],
	[50.412962, 30.644708],
	[50.412890, 30.644699],
	[50.412841, 30.644794],
	[50.412792, 30.644889],
	[50.412743, 30.644984],
	[50.412694, 30.645078],
	[50.412645, 30.645173],
	[50.412596, 30.645268],
	[50.412596, 30.645268],
	[50.412596, 30.645268],
	[50.412596, 30.645268],
	[50.412499, 30.645334],
	[50.412401, 30.645399],
	[50.412304, 30.645465],
	[50.412207, 30.645531],
	[50.412109, 30.645596],
	[50.412012, 30.645662],
	[50.411914, 30.645725],
	[50.411817, 30.645788],
	[50.411720, 30.645851],
	[50.411622, 30.645914],
	[50.411524, 30.645977],
	[50.411427, 30.646040],
	[50.411250, 30.646148],
	[50.411073, 30.646257],
	[50.410896, 30.646365],
	[50.410718, 30.646473],
	[50.410541, 30.646582],
	[50.410364, 30.646690],
	[50.410364, 30.646690],
	[50.410364, 30.646690],
	[50.410228, 30.646769],
	[50.410092, 30.646849],
	[50.409956, 30.646929],
	[50.409819, 30.647008],
	[50.409683, 30.647087],
	[50.409547, 30.647167],
	[50.409407, 30.647253],
	[50.409267, 30.647339],
	[50.409126, 30.647424],
	[50.408986, 30.647510],
	[50.408846, 30.647596],
	[50.408706, 30.647682],
	[50.408576, 30.647757],
	[50.408446, 30.647832],
	[50.408316, 30.647907],
	[50.408186, 30.647982],
	[50.408056, 30.648057],
	[50.407926, 30.648132],
	[50.407801, 30.648205],
	[50.407675, 30.648279],
	[50.407550, 30.648352],
	[50.407425, 30.648425],
	[50.407299, 30.648499],
	[50.407174, 30.648572],
	[50.407024, 30.648661],
	[50.406874, 30.648749],
	[50.406724, 30.648838],
	[50.406575, 30.648927],
	[50.406425, 30.649015],
	[50.406275, 30.649104],
	[50.406275, 30.649104],
	[50.406275, 30.649104],
	[50.406187, 30.649164],
	[50.406098, 30.649224],
	[50.406010, 30.649284],
	[50.405922, 30.649343],
	[50.405833, 30.649403],
	[50.405745, 30.649463],
	[50.405622, 30.649535],
	[50.405499, 30.649606],
	[50.405376, 30.649678],
	[50.405253, 30.649749],
	[50.405130, 30.649821],
	[50.405007, 30.649892],
	[50.404879, 30.649973],
	[50.404752, 30.650053],
	[50.404624, 30.650134],
	[50.404496, 30.650214],
	[50.404369, 30.650295],
	[50.404241, 30.650375],
	[50.404145, 30.650455],
	[50.404049, 30.650536],
	[50.403954, 30.650616],
	[50.403858, 30.650696],
	[50.403762, 30.650777],
	[50.403666, 30.650857],
	[50.403574, 30.650903],
	[50.403483, 30.650949],
	[50.403391, 30.650994],
	[50.403299, 30.651040],
	[50.403208, 30.651086],
	[50.403116, 30.651132],
	[50.403116, 30.651132],
	[50.403116, 30.651132],
	[50.402944, 30.651192],
	[50.402773, 30.651251],
	[50.402602, 30.651311],
	[50.402430, 30.651371],
	[50.402259, 30.651430],
	[50.402087, 30.651490],
	[50.401921, 30.651567],
	[50.401754, 30.651644],
	[50.401588, 30.651721],
	[50.401421, 30.651798],
	[50.401255, 30.651875],
	[50.401088, 30.651952],
	[50.400942, 30.652006],
	[50.400796, 30.652059],
	[50.400650, 30.652113],
	[50.400505, 30.652167],
	[50.400359, 30.652220],
	[50.400213, 30.652274],
	[50.400159, 30.652163],
	[50.400106, 30.652052],
	[50.400052, 30.651941],
	[50.399998, 30.651830],
	[50.399945, 30.651719],
	[50.399891, 30.651608],
	[50.399963, 30.651463],
	[50.400035, 30.651318],
	[50.400106, 30.651173],
	[50.400178, 30.651029],
	[50.400250, 30.650884],
	[50.400322, 30.650739],
	[50.400404, 30.650835],
	[50.400485, 30.650931],
	[50.400567, 30.651027],
	[50.400649, 30.651122],
	[50.400730, 30.651218],
	[50.400812, 30.651314],
	[50.400812, 30.651314],
	[50.400812, 30.651314]
]
tab_data_map_len = len(tab_data['map'])

# notification tab:
tab_data['note'] = ""

###

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QStatusBar, QLabel, QGridLayout, QScrollArea, QFrame, QDialog, QTabBar, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter
from PyQt5.QtCore import pyqtSlot, QTimer, QSize, QPoint, QMargins, Qt, QRect
from PyQt5.QtWebKitWidgets import QWebView
from time import localtime, strftime
import time
import locale
import os.path
import threading
from collections import OrderedDict
from gps3.agps3threaded import AGPS3mechanism

tabs = OrderedDict(
    bort  = dict(index=0, title="Борт",    tip="Панель виклику, датчики"),
    stop  = dict(index=1, title="Зупинки", tip="Графік руху, затримки"),
    route = dict(index=2, title="Маршрут", tip="Опис маршруту, загальна інформація"),
    map   = dict(index=3, title="Карта",   tip="Гугл карта руху транспортного засобу"),
    note  = dict(index=4, title="",        tip="Повідомлення")
)
tabs.move_to_end('bort')
tabs.move_to_end('stop')
tabs.move_to_end('route')
tabs.move_to_end('map')
tabs.move_to_end('note')

# base geom
WIN_SIZE = QSize(1024, 768)
ICON_SIZE = QSize(55, 80)
TABS_W = (215, 260, 260, 215, 65)

# colors
SBAR_COLOR = dict(bg="white", lag="#d62727", lead="#8ac349")
STOP_COLOR = dict(red="#d62727", green="#8ac349", blue="#0966ae", gray="#818181")

# fonts/styles
BG_STYLE = "background-color:#e9e6e4;"
FFAMILY = "font-family:arial,sans-serif;"   # font family
SPRFX = FFAMILY + "font-weight:bold;"
TAB_STYLE = dict(tab=BG_STYLE+SPRFX+"font-size:27px; color:#2c2c2c; border-top-left-radius:10px; border-top-right-radius:10px; margin: 9px 0 0 9px; height:70px;", content="background-color:white;")
SBAR_STYLE = SPRFX + "font-size:26px;"
MAIN_STYLE = dict(bg="background:qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #56b2b1, stop:1 #aed468);",
    btn="border-radius:20px; background:rgba(0,74,57,0.5); color:white; font-size:27px; font-weight:bold;",
    cnt=SPRFX+"font-size:105px;", col1="color:#77fffe;",
    col2="color:#c8ff89;", col3="color:#ff8989;")
NMSG_STYLE = dict(mesg="border-top-right-radius:5px; border-bottom-right-radius:5px; font-size:24px; padding:0 15px;",
    date="border-top-left-radius:5px; border-bottom-left-radius:5px; font-size:26px; font-weight:bold;")
NMSG_COLOR = dict(date="#72bd79", mesg="#d6efbb")
WH_COLOR = ["#f7f3e6", "#efebdd"]

BORT_STYLE = "background:qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #a1d1d1, stop:1 #cfe2ab); background-repeat:no-repeat; background-position:center;"
BORT_BTN_STYLE = dict(base="border-radius:5px; color:" + WH_COLOR[0] + "; font-size:19px; font-weight:bold; margin-bottom:9px;",
    bg_gr="background: qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #55b271, stop:1 #168b58);",
    bg_rd="background: qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #c87858, stop:1 #c03232);")
STOP_STYLE = dict(name=SPRFX+"font-size:26px;", delay=SPRFX+"font-size:36px;")
ROUTE_STYLE = dict(item=SPRFX+"font-size:24px;", desc=FFAMILY+"font-size:24px;")
NOTE_STYLE = dict(mesg=SPRFX+"font-size:30px; qproperty-alignment:AlignTop; qproperty-wordWrap:true;",
    date=SPRFX+"font-size:21px; qproperty-alignment:AlignJustify;",
    btn=SPRFX+"font-size:26px; border-radius: 5px;",
    btn_ok="background:#4c9d5d; color:#fff;",
    btn_all="background: #d8d8d8; color:#2c2c2c;",
    btn_wo="background: #c45143; color:#f7f3e6;")

# images
IMAGE_DIR = "/opt/telecard/images/" # image folder
TAB_ICO_PRFX = "ico50x70-"
TAB_ICO_SFFX = dict(selected="_a.png", unselected="_p.png")
SBAR_ICO = dict(logo="logo00.png", clock="ico-time0.png")
STOP_ICO = dict(top="a2.png", between="b2.png", bottom="c2.png", bort="bus_g0.png")
RT_SEP = "rt-sep1.png"
BORT_ICO = dict(prfx="ico-vh-btn", bort="tram07.png", gps="gps.png",
    sensors=dict(bkts="bkts.png", mob="mobile-terminal.png", val="validator.png"))

# misc settings
DEFAULT_TAB = 0  # 0 - Трансп.засіб
STOP_TAB = 1     # 1 - Зупинки
ROUTE_TAB = 2    # 2 - Маршрут
MAP_TAB = 3      # 3 - Карта
MESSAGE_TAB = 4  # 4 - Повідомлення
PANE_PAD = 9   # pane paddings
ROUTE_SH = (32, 35)     # tab route: stretches
STOP_SH = (1, 4, 2, 2)  # tab stop: stretches, vertical spacing
STOP_VS = 2
GREY_LAG = -100 # lag minimum
BORT_BTN = ("Розпочати рейс", "Тривога", "Викликати оператора")


### misc
messages = [
    dict(status=1, date='27.05.2017 10:05', mesg='Нове повідомлення від диспетчера. Ви рухаєтесь із запізненням 3 хвилини.'),
    dict(status=1, date='27.05.2017 09:30', mesg='Увага, на вулиці Т.Шевченка сталася дорожно-транспортна пригода. Рух транспорту уповільнено.'),
    dict(status=0, date='27.05.2017 08:55', mesg='Нове повідомлення від диспетчера. Ви рухаєтесь із запізненням 3 хвилини.'),
    dict(status=0, date='27.05.2017 07:20', mesg='Нове повідомлення від диспетчера. Ви рухаєтесь із запізненням 2 хвилини.')
]
active_tab = DEFAULT_TAB
agps = None
NA = "n/a"
bort_started_at = 0


### complimentary funcs

class Label05(QLabel):
    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setOpacity(0.5)
        painter.drawPixmap(QPoint(0, 0), self.pixmap())
        painter.end()

def tab_bort_sensor(vh, ico, status, i, y0, sz = None, dx = None):
    PAD = (40, 130)
    BG = "background:transparent;"
    if sz is not None:
        SW = (WIN_SIZE.width()-(PAD[0]+PAD[1]))/sz
    l = Label05(vh) if status is "no" else QLabel(vh)
    l.setStyleSheet(BG)
    lico = QPixmap(IMAGE_DIR + ico)
    x0 = dx if dx is not None else PAD[0]+SW*i+(SW-lico.width())/2
    l.setPixmap(lico)
    l.move(x0, y0)
    s = QLabel(vh)
    s.setStyleSheet(BG)
    sico = QPixmap(IMAGE_DIR + "sensor-" + status + ".png")
    s.setPixmap(sico)
    if dx is None:
        s.move(x0+lico.width()-sico.width()/2, y0-sico.height()/2)
    else:
        s.move(x0-sico.width()/2, y0+lico.height()-sico.height())

def tab_bort_start(e, w):
    global bort_started_at
    bort_started_at = time.time()
    tw.setCurrentIndex(MAP_TAB)

def tab_bort(tab, data):
    grid = QGridLayout()
    grid.setSpacing(0)
    grid.setContentsMargins(PANE_PAD, PANE_PAD, PANE_PAD, 0)

    for i, v in enumerate(BORT_BTN):
        b = QPushButton(" " + v)
        b.setFixedSize(320, 80)
        bg = BORT_BTN_STYLE['bg_rd'] if i % 2 else BORT_BTN_STYLE['bg_gr']
        b.setStyleSheet(BORT_BTN_STYLE['base'] + bg)
        b.setIcon(QIcon(IMAGE_DIR + BORT_ICO['prfx'] + str(i+1) + ".png"))
        b.setIconSize(QSize(28, 28))
        if i is 0:
            align = Qt.AlignLeft
        elif i is len(BORT_BTN) - 1:
            align = Qt.AlignRight
        else:
            align = Qt.AlignHCenter
        if (i == 0):    # start a race
            b.clicked.connect(lambda e, t=tab: tab_bort_start(e, t))
        grid.addWidget(b, 0, i, alignment=align)

    bort = QWidget()
    bort.setStyleSheet(BORT_STYLE + "background-image:url(" + IMAGE_DIR + BORT_ICO['bort'] + ");")

    sensors = [ BORT_ICO['sensors']['bkts'], BORT_ICO['sensors']['mob'], BORT_ICO['sensors']['val'],
        BORT_ICO['sensors']['val'], BORT_ICO['sensors']['val'], BORT_ICO['sensors']['mob'],
        BORT_ICO['sensors']['bkts'] ]
    l = len(sensors)
    sstatus = (0, 1, 1, 0, 1, 0, 1) # temp
    dy = 160
    for i, v in enumerate(sensors):
        ss = "no" if sstatus[i] is 0 else "ok"
        tab_bort_sensor(bort, v, ss, i, dy + 125, sz = l)
    tab_bort_sensor(bort, BORT_ICO['gps'], "ok", 0, dy, dx=805)

    grid.addWidget(bort, 1, 0, 1, 3)
    tab.setLayout(grid)
tabs['bort']['func'] = tab_bort

ts_grid = None
def tab_stop_elem(item, row, col, align = Qt.AlignHCenter, fc = None, style = ""):
    fcs = "color:" + fc + ";" if fc is not None else ""
    item.setAlignment(align | Qt.AlignVCenter)
    item.setStyleSheet(style + BG_STYLE + fcs)
    ts_grid.addWidget(item, row, col)
    return (col + 1)

def tab_stop_line(i, v, ico):
    lmg = QLabel()
    lmg.setPixmap(QPixmap(IMAGE_DIR + ico))
    col = tab_stop_elem(lmg, i, 0)

    ttl = QLabel(v['name'])
    col = tab_stop_elem(ttl, i, col, align = Qt.AlignLeft, style = STOP_STYLE['name'])

    if v['schedule'] is 0:
        dl1 = QLabel()
        dl1.setPixmap(QPixmap(IMAGE_DIR + STOP_ICO['bort']))
        fc = None
    else:
        dl1 = QLabel(str(v['schedule']) + 'хв')
        fc = STOP_COLOR['red'] if v['schedule'] < 0 else STOP_COLOR['blue']
    col = tab_stop_elem(dl1, i, col, fc = fc, style = STOP_STYLE['delay'])

    (lag, fc) =  ('--', STOP_COLOR['gray']) if v['lag'] < GREY_LAG else (
            str(v['lag']) + 'хв', STOP_COLOR['green'] if v['lag'] is 0 else (
                STOP_COLOR['red'] if v['lag'] < 0 else STOP_COLOR['blue']))
    dl2 = QLabel(lag)
    col = tab_stop_elem(dl2, i, col, fc = fc, style = STOP_STYLE['delay'])

def tab_stop_body(data):
    global ts_grid
    while ts_grid.count():
        ts_grid.takeAt(0).widget().deleteLater()
    tab_stop_line(0, data[0], STOP_ICO['top'])
    for (i, v) in enumerate(data[1:-1]):
        tab_stop_line(i+1, v, STOP_ICO['between'])
    l = len(data) - 1
    tab_stop_line(l, data[l], STOP_ICO['bottom'])

def tab_stop(tab, data):
    global ts_grid
    layout = QVBoxLayout()
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    content = QWidget()

    ts_grid = QGridLayout()
    ts_grid.setAlignment(Qt.AlignTop)
    ts_grid.setHorizontalSpacing(0)
    ts_grid.setVerticalSpacing(STOP_VS)
    tab_stop_body(data)
    for (i, v) in enumerate(STOP_SH):
        ts_grid.setColumnStretch(i, v)

    content.setLayout(ts_grid)
    scroll.setWidget(content);
    layout.addWidget(scroll)
    tab.setLayout(layout)
tabs['stop']['func'] = tab_stop


def tab_route_line(grid, i, v, last = False):
    padt = PANE_PAD if i is 0 else 1
    padb = PANE_PAD if last is True else 1
    pad = "padding-top:" + str(padt) + ";padding-bottom:" + str(padb) + ";"

    item = QLabel(v['item'])
    item.setStyleSheet(ROUTE_STYLE['item'] + BG_STYLE + pad + "padding-left:" + str(WIN_SIZE.width()/5+10) + ";")
    grid.addWidget(item, i, 0)

    desc = QLabel(v['desc'])
    desc.setStyleSheet(ROUTE_STYLE['desc'] + BG_STYLE + pad)
    grid.addWidget(desc, i, 1)

    if last is False:
        dl = QLabel()
        dl.setPixmap(QPixmap(IMAGE_DIR + RT_SEP))
        dl.setStyleSheet(BG_STYLE)
        dl.setAlignment(Qt.AlignCenter);
        grid.addWidget(dl, i+1, 0, 1, 2)

def tab_route(tab, data):
    grid = QGridLayout()
    grid.setSpacing(0)
    grid.setContentsMargins(PANE_PAD, PANE_PAD, PANE_PAD, 0)
    for (i, v) in enumerate(data[0:-1]):
        tab_route_line(grid, i*2, v)
    l = len(data) - 1
    tab_route_line(grid, l*2, data[l], last = True)
    for (i, v) in enumerate(ROUTE_SH):
        grid.setColumnStretch(i, v)
    tab.setLayout(grid)
tabs['route']['func'] = tab_route

webmap = ""

html = '''
<html><head></head><body>
<script src="http://maps.googleapis.com/maps/api/js?libraries=geometry"></script>
<script>
        var stop0 = new google.maps.LatLng(50.400812, 30.651314);
        var stops = [ [ // forward
{ lat:50.400812, lng:30.651314, title:"ст. м. Харківська (кінцева)", delay:"0 min"},
{ lat:50.402266, lng:30.651657, title:"Ринок (на вимогу)",   delay:"1 min"},
{ lat:50.406364, lng:30.649954, title:"вул. Кошиця",         delay:"2 min"},
{ lat:50.410461, lng:30.647461, title:"вул. Олійника",       delay:"3 min"},
{ lat:50.414490, lng:30.644903, title:"вул. Тростянецька",   delay:"4 min"},
{ lat:50.416416, lng:30.643942, title:"Магазин (на вимогу)", delay:"5 min"},
{ lat:50.419909, lng:30.641861, title:"вул. Російська",      delay:"6 min"},
{ lat:50.424359, lng:30.644092, title:"вул. Новодарницька",  delay:"7 min"},
{ lat:50.423042, lng:30.644088, title:"ш. Харківське",       delay:"8 min"},
], [    // reverse
{ lat:50.423042, lng:30.644088, title:"ш. Харківське",       delay:"9 min"},
{ lat:50.422324, lng:30.641159, title:"вул. Ревуцького",     delay:"10 min"},
{ lat:50.419878, lng:30.641198, title:"вул. Російська",      delay:"11 min"},
{ lat:50.415848, lng:30.643302, title:"Озеро Сонячне",       delay:"12 min"},
{ lat:50.412012, lng:30.645662, title:"вул. Анни Ахматової", delay:"13 min"},
{ lat:50.410364, lng:30.646690, title:"вул. Олійника",       delay:"14 min"},
{ lat:50.406275, lng:30.649104, title:"вул. Кошиця",         delay:"15 min"},
{ lat:50.403116, lng:30.651132, title:"ст. м. Харківська",   delay:"16 min"},
{ lat:50.400812, lng:30.651314, title:"ст. м. Харківська (кінцева)", delay:"17 min"},
]]

        var directions = new google.maps.DirectionsService();
        var bounds;
        var map;

        function map_stops(stop, len, icol, ecol) {
            var erender = new google.maps.DirectionsRenderer({
                suppressMarkers: true,
                polylineOptions: {
                    strokeColor: ecol,
                    strokeWeight: 7
                },
                map: map
            });
            var irender = new google.maps.DirectionsRenderer({
                suppressMarkers: true,
                polylineOptions: {
                    strokeColor: icol,
                    strokeWeight: 4
                },
                map: map
            });
            bounds = new google.maps.LatLngBounds();
            var request = {
                origin: { lat:stop[0].lat, lng:stop[0].lng},
                destination: { lat:stop[len-1].lat, lng:stop[len-1].lng},
                travelMode: google.maps.TravelMode.DRIVING,
                waypoints: []
            }
            var info = new google.maps.InfoWindow();
            for (i = 0; i < len; i++) {
                var marker = new google.maps.Marker({
                    position: { lat:stop[i].lat, lng:stop[i].lng},
                    title: stop[i].title,
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        strokeWeight: 2.7,
                        strokeOpacity: 0.8,
                        fillColor: "#fff",
                        fillOpacity: 1,
                        scale: 4.7
                    },
                    map: map
                });
                bounds.extend(marker.position);
                (function(m, s) {
                    google.maps.event.addListener(marker, "click", function (e) {
                        info.setContent(s.title + ", " + s.delay);
                        info.open(map, m);
                    });
                })(marker, stop[i]);
            }
            for (i = 1; i < len - 1; i++) {
                request.waypoints.push({
                    location: { lat:stop[i].lat, lng:stop[i].lng},
                    stopover: true
                });
            }
            map.fitBounds(bounds);
            directions.route(request, function(result, status) {
                if (status == google.maps.DirectionsStatus.OK) {
                    erender.setDirections(result);
                    irender.setDirections(result);
                }
            });
        }

        var bus;
        function moveBus(lat, lng) {
            var pos = new google.maps.LatLng(lat, lng);
            if (pos.equals(stop0)) {
                map.setCenter({lat:50.4055, lng:30.654});
                map.setZoom(15);
            }
            if (!map.getBounds().contains(pos)) {
                map.panTo({lat:pos.lat(), lng:pos.lng()});
            }
            bus.setPosition(pos);
        };

        window.onload = function() {
            map = new google.maps.Map(document.getElementById("drv-map"), {
                mapTypeId: google.maps.MapTypeId.ROADMAP,
            });
            map_stops(stops[0], stops[0].length, "#00b3fd", "#1f7cb6");
            map_stops(stops[1], stops[1].length, "#ff9e00", "#ac7413");
            bus = new google.maps.Marker({
                position: { lat:stops[0][0].lat, lng:stops[0][0].lng},
                title: 'Bus #7218',
                icon: {
                    url:"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAbCAYAAABiFp9rAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QgIDAgAJctyxQAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAE+ElEQVRIx7WWf0zUZRzHX8/3vnccyN0B8lOkEAV/jASxmOSQX6UUkqbmLHM5U8zGajbbqlWrPzJq003TaaitJaQzGxN/DGuKxlTUQYoURmoISAnHr7sDjrv73rc/kJ9yaG69n/+ez+fzvD8/n+cReMKyJDh8AVbMjcHomwHaFFQRAcLYp6BaEGoDOM/Saj3Jj+dvDdiMAuGRaEVyDCbT5zqdedy6pzrUtQnX6+LD8UGPHwB2Oq7coXtv5bRJ+Zf9cDoCu+jsfJ+DZbUPJoqPhCt1iA3PfShruzMPLb9cvzihOxgHKqB6cEmgQxRV+txdfijxccWhP6buLsnrP+t+oj6BJDYs3D816Ka+5oMaHXa8+C/Q0zt98wzHHy1RdnXXsVXER7r7yYZH9EZWYWrUBXtpblsEDh4NOkjbEdBw5laSnt3HV/ZvSwOh5czfGDnebCrNbQt/ZBIAB5TmtoVHBrQYRc78jYOpS4uDIMNk/HV71S2nW3FhHGbojbu5Aa/i4/jfbkRvtSErCui9UAPH40iIw/ZsNu10IQ2rogar2JQeQLtjLS3Wm32py3n+m22LLnm/NdccOLToioJIySL+XDmBYwUhy6iFe/h1+VJacQ/Wf/u5QPPbRxJ7yD+xRpA5O5wo3wJ1y9leegdTCfBpHhGf5DHtYTImSaiKQgmdyAObXijinVQf6qyvyEQEZL42658eHOhgiD+AuRWd0YBzy2fU2Hs9z9ylCkz7D/LYKPXSrpzVZit0hjwjI7zmrZt9rRGVyFHOUPV63GtzacKCxhNRvg51VCIV9+uzqpoKKxZmSKgicu5kDPxPSIvBF0VMlEEY0dLhqaUVBdHwO942m+eImpvReWTS4o0Qxj4iDVpPem3t6KYkkDyW1273WF2CjBD+Mrjv0IsFCBhNT1XB6URSPdx0Oh1ul2t4tw5DL1ZUd5MEWNssWMeakXMnKS8qoGKkLCmR1ltXKFuSTZMn+1YLFgQWCeGs3nEx1H/Ua1kCWcb9ZAK2+Jl0jZQHB9EbPp3uieH0eCL66mJYMDirJRSlqPBqsBPNkEG7h+QkOu12NIFRpMTO4emR8uITTAgOIn3nHqKiJ2NFGTFrGuQDVUF2FKVIZt/P5bXrs7dbbFXXjd6EDtV7aRXNhlycFgvapERaJ4RhH5ZWDeqxEkIVBZGzmnpGdKbVRkPt3cgn2Fdc3heF0rvzxe9jF5/KqZZRcA0ZOGEw4LLa0G7+mBupKViGeeyDO24mhqrfMIWG4BwZTXZBrBHFvm34e7Q+u6xkTentBVNtIf0Xq6qC8EMBVKzIjNbGBhQkVLrQ4Bo4T/xU69u8YF9aOF8fTR0kWp0OkhSIJJ/4+6OS2hATIcLz0z0mVBB1Zlqi8jKn4HZl4VJa+K50RPFeTp6Hj+6La5vO3IgNU8JGXrIPhEBz7Y6mcebW1Gi6HO9xoOyXwUwORXX9bSKDK3ddjVtl1JtvJkX3GO7rJM9PuPrlqYD6pfszZmBuf5Mfzl988HdrdXogXvqt3t5dYQXLLjQvSXCYcKFHvbf6LPuWjL2oUtf56uGkkO7ucQ047O/y7Wnzw/3r0uKg9CrkZJ2StR0x2VNthhdm/NU5e6Jb4zPOrQfo7pLsFY2ScrRmkqn4uq/V5fSrJf94xoDtQ38gARbNgSPlkLNgA6pmEUjRIPT3ym4H958I5Qj5J3cN6HrAv9if6YkC6xivAAAAAElFTkSuQmCC",
                    anchor: new google.maps.Point(13, 14)
                },
                optimized: false,
                zIndex:999,
                map: map
            });
        }
</script>
<div id="drv-map" style="width: 100%; height: 100%;"></div>
</body>
</html>
'''

def tab_map(tab, data):
    global webmap
    webmap = QWebView()
    webmap.setHtml(html)
    layout = QVBoxLayout()
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(webmap)
    tab.setLayout(layout)
tabs['map']['func'] = tab_map


def tab_note_uncheck(ev, i, l1, l2):
    global messages
    l1.setStyleSheet(NMSG_STYLE['date'] + "background:" + WH_COLOR[1] + ";")
    l1.mousePressEvent = None
    l2.setStyleSheet(NMSG_STYLE['mesg'] + "background:" + WH_COLOR[0] + ";")
    l2.mousePressEvent = None
    messages[i]['status'] = 0   # it's read

def tab_note_elem(m, tag, mw, color, align = None):
    mh = 130
    bg = color if m['status'] is 0 else NMSG_COLOR[tag]
    txt = m[tag] if align is None else '<p align="center">' + m[tag] + '</p>'
    l = QLabel(txt)
    l.setStyleSheet(NMSG_STYLE[tag] + "background:" + bg + ";")
    l.setFixedSize(mw, mh)
    l.setWordWrap(True)
    return l

def tab_note_line(grid, i, m):
    l1 = tab_note_elem(m, 'date', 192, WH_COLOR[1], True)
    grid.addWidget(l1, i, 0)
    l2 = tab_note_elem(m, 'mesg', 800, WH_COLOR[0])
    grid.addWidget(l2, i, 1)
    if m['status'] is not 0:
        l1.mousePressEvent = lambda ev: tab_note_uncheck(ev, i, l1, l2)
        l2.mousePressEvent = lambda ev: tab_note_uncheck(ev, i, l1, l2)

def tab_note(tab, data):
    layout = QVBoxLayout()
    layout.setSpacing(0)
    layout.setContentsMargins(PANE_PAD, PANE_PAD, PANE_PAD, 0)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    content = QWidget()
    content.setStyleSheet("margin-bottom:6px;")
    content.setContentsMargins(0, 0, 0, 0)

    grid = QGridLayout()
    grid.setSpacing(0)
    grid.setContentsMargins(0, 0, 0, 0)
    for i, m in enumerate(messages):
        tab_note_line(grid, i, m)

    content.setLayout(grid)
    scroll.setWidget(content);
    layout.addWidget(scroll)
    tab.setLayout(layout)
tabs['note']['func'] = tab_note


def show_time():
    global tm_label
    tm_label.setText(strftime("%H:%M", localtime()))


LL_RANGE = dict(lat=(40.0, 60.0), lon=(20.0, 40.0)) # [40..60] and [20..50] limits for LatLng
last_ll = dict(lat=0.0, lon=0.0, new=False)

def chk_latlng():
    global agps, last_ll
    lat, lon = agps.data_stream.lat, agps.data_stream.lon
    if isinstance(lat, float) and isinstance(lon, float):
        if (lat != last_ll['lat']) or (lon != last_ll['lon']):
            if (LL_RANGE['lat'][0] < lat < LL_RANGE['lat'][1]) and (LL_RANGE['lon'][0] < lon < LL_RANGE['lon'][1]):
                last_ll = dict(lat=lat, lon=lon, new=True)
            else:
                print("LatLng(", lat, ",", lon, ") is out of range:", LL_RANGE)

# just demo
demo_cnt = 0
demo_ts_data = [
    # Column1 = name, Column2  = schedule, Column3 = lag
    #   lag colors: positive is blue, zero is green, negative is red (le -1000 is grey)
    dict(name="1st- ст. м.",          schedule=28, lag=-5),
    dict(name="2nd - Ринок",          schedule=29, lag=4),
    dict(name="3rd - Кошиця",         schedule=31, lag=-3),
    dict(name="4th - Олійника",       schedule=33, lag=1),
    dict(name="5th - Тростянецька",   schedule=0,  lag=-1000),   # <= GREY_LAG: unknown
    dict(name="6th - Магазин",        schedule=43, lag=0),
    dict(name="7th - Російська",      schedule=44, lag=-1000),
    dict(name="8th - Новодарницька",  schedule=46, lag=1),
    dict(name="new - Нвдрнцк",        schedule=46, lag=0),
    dict(name="lst - Харківське",     schedule=47, lag=1),
]
# demo end

def local_exec():   # every 1sec
    global webmap, active_tab, last_ll
#    chk_latlng() # location update

# just demo
    global demo_cnt
    demo_cnt += 1
# demo end


    if active_tab is MAP_TAB:
        if bort_started_at:
#        if last_ll['new']:
#            webmap.page().mainFrame().evaluateJavaScript("moveBus(" + str(last_ll['lat']) + "," + str(last_ll['lon']) +")")
#            last_ll['new'] = False
            ndx = (int(time.time()-bort_started_at)) % tab_data_map_len
            la, lo = str(tab_data['map'][ndx][0]), str(tab_data['map'][ndx][1])
            webmap.page().mainFrame().evaluateJavaScript("moveBus("+la+","+lo+")")
# just demo
    elif active_tab is STOP_TAB:
        if (demo_cnt % 60) == 0:
            tab_stop_body(tab_data['stop'])
        elif (demo_cnt % 60) == 30:
            tab_stop_body(demo_ts_data)
# demo end
# demo2
    global sb_driver, sb_route, sb_delay
    if (demo_cnt % 20) == 0:
        sb_driver.setText("Validator F.S.")
        sb_route.setText("R99")
        dly = int(demo_cnt/45)%10
        if (dly % 2) == 0:
            dly = -dly
        sb_delay.setText(str(dly) + 'хв')
        sb_delay.setStyleSheet(SBAR_STYLE + "color:" + (SBAR_COLOR['lag'] if dly < 0 else SBAR_COLOR['lead']) + ";")
# demo2 end


def statusbar(w):
    global tm_label, tm, sb_driver, sb_route, sb_delay
    SB_MARGINS = dict(driver=QMargins(30, 0, 45, 0), route=QMargins(40, 0, 55, 0),
            clock=QMargins(10, 2, 0, 2), delay=QMargins(10, 0, 30, 0), time=QMargins(70, 0, 40, 0),
            logo=QMargins(0, 0, 10, 0))

    sb = QStatusBar()
    w.setStatusBar(sb)
    sb.setStyleSheet("QStatusBar { background:" + SBAR_COLOR['bg'] + ";}")

    sb_driver = QLabel(data['statusbar']['driver'])
    sb_driver.setContentsMargins(SB_MARGINS['driver'])
    sb_driver.setStyleSheet(SBAR_STYLE)
    sb_driver.setFixedWidth(250)
    w.statusBar().addWidget(sb_driver)

    sb_route = QLabel(data['statusbar']['route'])
    sb_route.setContentsMargins(SB_MARGINS['route'])
    sb_route.setStyleSheet(SBAR_STYLE)
    sb_route.setFixedWidth(180)
    w.statusBar().addWidget(sb_route)

    l = QLabel()
    l.setPixmap(QPixmap(IMAGE_DIR + SBAR_ICO['clock']))
    l.setContentsMargins(SB_MARGINS['clock'])
    w.statusBar().addWidget(l)

    dly = data['statusbar']['delay']
    sb_delay = QLabel(str(dly) + 'хв')
    sb_delay.setContentsMargins(SB_MARGINS['delay'])
    sb_delay.setStyleSheet(SBAR_STYLE + "color:" + (SBAR_COLOR['lag'] if dly < 0 else SBAR_COLOR['lead']) + ";")
    w.statusBar().addWidget(sb_delay)

    tm_label = QLabel(strftime("%H:%M", localtime()))
    tm_label.setStyleSheet(SBAR_STYLE)
    tm_label.setContentsMargins(SB_MARGINS['time'])
    w.statusBar().addWidget(tm_label)

    tm = QTimer()
    tm.timeout.connect(show_time)
    tm.start(5000)

    l = QLabel()
    l.setPixmap(QPixmap(IMAGE_DIR + SBAR_ICO['logo']))
    l.setContentsMargins(SB_MARGINS['logo'])
    w.statusBar().addPermanentWidget(l)


def splashnote_ok(e, d):
    d.close()

def splashnote(w, tw, last):
    DIALOG_SZ = QSize(350, 270)
    MS_RECT = QRect(0,  40, DIALOG_SZ.width(), 100)
    DT_RECT = QRect(0, 150, DIALOG_SZ.width(), 50)
    OK_RECT = QRect(16, 220, 318, 36)
    OK_TEXT = "Вхід без реєстраціїї"

    d = QWidget(w, Qt.FramelessWindowHint)
    d.setStyleSheet("border-radius:10px; background-color:" + WH_COLOR[0] + ";")
    d.resize(DIALOG_SZ.width(), DIALOG_SZ.height())
    d.move((WIN_SIZE.width()-DIALOG_SZ.width())/2, (WIN_SIZE.height()-DIALOG_SZ.height())/2 +30)

    ms = QLabel("<p align='center'>%s</p>" % last['mesg'], d)
    ms.setGeometry(MS_RECT)
    ms.setStyleSheet(NOTE_STYLE['mesg'])

    dt = QLabel("<p align='center'>%s</p>" % last['date'], d)
    dt.setGeometry(DT_RECT)
    dt.setStyleSheet(NOTE_STYLE['date'])

    ok = QPushButton(OK_TEXT, d)
    ok.setGeometry(OK_RECT)
    ok.setStyleSheet(NOTE_STYLE['btn'] + NOTE_STYLE['btn_wo'])
    ok.setDefault(True)
    ok.clicked.connect(lambda e, dlg=d: splashnote_ok(e, dlg))

    d.show()


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        sz = super(TabBar, self).tabSizeHint(index)
        size = QSize(TABS_W[index], sz.height())
        return size

def change_tabico(ind, tw):
    global active_tab
    for tab in tabs:
        t = tabs[tab]
        state = 'unselected' if t['index'] is not ind else 'selected'
        if t['icons'][state] is not None:
            tw.setTabIcon(t['index'], t['icons'][state])
    active_tab = ind


### main
app = QApplication(sys.argv)
app.setStyleSheet("QStatusBar::item { border: 0px solid black;}")
window = QMainWindow()
window.setWindowFlags(Qt.FramelessWindowHint)
window.setFixedSize(WIN_SIZE)

# tabs
tw = QTabWidget()
tabbar = TabBar()
tw.tabBar().setExpanding(True)
tw.setTabBar(tabbar)
tw.setDocumentMode(True)

for tab in tabs:
    tw.setIconSize(ICON_SIZE)
    t = tabs[tab]
    i = t['index']
    w = QWidget()
    w.setStyleSheet(TAB_STYLE['content'])
    t['icons'] = {}
    for sffx in TAB_ICO_SFFX:
        fname = IMAGE_DIR + TAB_ICO_PRFX + tab + TAB_ICO_SFFX[sffx]
        t['icons'][sffx] = QIcon(fname) if os.path.isfile(fname) else None
    ico = t['icons']['unselected' if i is not DEFAULT_TAB else 'selected']
    if ico is None:
        tw.insertTab(i, w, t['title'])
    else:
        tw.insertTab(i, w, ico, t['title']+'   ')
    tw.setTabToolTip(i, t['tip'])
    t['func'](w, tab_data[tab])
tw.setStyleSheet("QTabBar::tab {" + TAB_STYLE['tab'] + "}" +
        "QTabBar::tab:selected {background-color: #fff;}" +
        "QTabWidget::tab-bar {/*left:20px;*/width:9999px;}")
tw.tabBar().setStyleSheet("background-color: #4c9d86;");
tw.currentChanged.connect(lambda i, t=tw: change_tabico(i, t))
tw.setCurrentIndex(DEFAULT_TAB)
window.setCentralWidget(tw)

statusbar(window)
window.show()

#for m in messages:
#    if m['status'] is not 0:
#        splashnote(window, tw, m)
#        break
splash_dt = strftime("    %T<br>%A, %B %d, %Y", localtime())
splashnote(window, tw, dict(mesg="Зареєструйтесь,<br>будь ласка!", date=splash_dt.title()))

agps = AGPS3mechanism()
agps.stream_data()
agps.run_thread()
timer = QTimer()
timer.timeout.connect(local_exec)
timer.start(1000)

sys.exit(app.exec_())

