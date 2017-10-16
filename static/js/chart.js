zingchart.MODULESDIR = 'https://cdn.zingchart.com/modules/';
ZC.LICENSE = ['569d52cefae586f634c54f86dc99e6a9', 'ee6b7db5b51705a13dc2339db3edaf6d'];

var myConfig = {
    type: 'line',
    backgroundColor: '#2C2C39',
    legend: {
        align: 'center',
        verticalAlign: 'top',
        backgroundColor: 'none',
        borderWidth: 0,
        item: {
            fontColor: '#E3E3E5',
            cursor: 'hand'
        },
        marker: {
            type: 'circle',
            borderWidth: 0,
            cursor: 'hand'
        }
    },
    plotarea: {
        margin: 'dynamic 70'
    },
    plot: {
        aspect: 'spline',
        lineWidth: 2,
        marker: {
            borderWidth: 0,
            size: 5
        }
    },
    scaleX: {
        lineColor: '#E3E3E5',
        zooming: true,
        //minValue: oasi_min_value,
        item: {
            fontColor: '#E3E3E5'
        },
        transform: {
            type: 'date',
            all: '%d.%m.%Y<br>%h:%i:%s'
        }
    },
    scaleY: {
        minorTicks: 1,
        lineColor: '#E3E3E5',
        tick: {
            lineColor: '#E3E3E5'
        },
        minorTick: {
            lineColor: '#E3E3E5'
        },
        minorGuide: {
            visible: false,
            lineWidth: 1,
            lineColor: '#E3E3E5',
            alpha: 0.7,
            lineStyle: 'dashed'
        },
        guide: {
            lineStyle: 'dashed'
        },
        item: {
            fontColor: '#E3E3E5'
        },
        format:'%v m3/s'
    },
    'scale-y-2': {
        minorTicks: 1,
        lineColor: '#E3E3E5',
        tick: {
            lineColor: '#E3E3E5'
        },
        minorTick: {
            lineColor: '#E3E3E5'
        },
        minorGuide: {
            visible: false,
            lineWidth: 1,
            lineColor: '#E3E3E5',
            alpha: 0.7,
            lineStyle: 'dashed'
        },
        guide: {
            lineStyle: 'dashed'
        },
        item: {
            fontColor: '#E3E3E5'
        },
        format:'%v mm'
    },
    tooltip: {
        borderWidth: 0,
        borderRadius: 3
    },
    preview: {
        adjustLayout: true,
        borderColor: '#E3E3E5',
        mask: {
            backgroundColor: '#E3E3E5'
        }
    },
    crosshairX: {
        plotLabel: {
            multiple: true,
            borderRadius: 3
        },
        scaleLabel: {
            backgroundColor: '#53535e',
            borderRadius: 3
        },
        marker: {
            size: 7,
            alpha: 0.5
        }
    },
    crosshairY: {
        lineColor: '#E3E3E5',
        type: 'multiple',
        scaleLabel: {
            decimals: 2,
            borderRadius: 3,
            offsetX: -5,
            fontColor: '#2C2C39',
            bold: true
        }
    },
    shapes: [{
        type: 'rectangle',
        id: 'view_all',
        height: '20px',
        width: '75px',
        borderColor: '#E3E3E5',
        borderWidth: 1,
        borderRadius: 3,
        x: '85%',
        y: '11%',
        backgroundColor: '#53535e',
        cursor: 'hand',
        label: {
            text: 'View All',
            fontColor: '#E3E3E5',
            fontSize: 12,
            bold: true
        }
    }],
    series: [{
        text: 'Deflusso OASI - Stabio',
        values: oasi_values,
        scales: 'scale-x, scale-y',
        lineColor: '#E34247',
        marker: {
            backgroundColor: '#E34247'
        }
    }, {
        text: 'Precipitationi CPC 60min - bacino imbriefero del Faloppia',
        values: cpc['accu_0060']['rain'],
        scales: 'scale-x, scale-y-2',
        lineColor: '#ffb52f',
        marker: {
            backgroundColor: '#ffb52f'
        }
    }, {
        text: 'Precipitationi CPC ultimi 30min - bacino imbriefero del Faloppia',
        values: cpc['accu_0060']['rain'],
        scales: 'scale-x, scale-y-2',
        lineColor: '#7D5918',
        marker: {
            backgroundColor: '#7D5918'
        }
    }, {
        text: 'Precipitationi CPC 12h - area di 20 x 20 Km attorno a Novazzano',
        values: cpc['accu_0720']['rain'],
        scales: 'scale-x, scale-y-2',
        lineColor: '#34BAAF',
        marker: {
            backgroundColor: '#34BAAF'
        }
    }, {
        text: 'Precipitationi CPC ultime 6h - area di 20 x 20 Km attorno a Novazzano',
        values: cpc['accu_0720']['rain'],
        scales: 'scale-x, scale-y-2',
        lineColor: '#246b62',
        marker: {
            backgroundColor: '#246b62'
        }
    }
    ]
};

zingchart.render({
    id: 'water_chart',
    data: myConfig,
    height: '500',
    width: '100%'
});

zingchart.shape_click = function (p) {
    if (p.shapeid == 'view_all') {
        zingchart.exec(p.id, 'viewall');
    }
}
