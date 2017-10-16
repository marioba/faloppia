zingchart.MODULESDIR = "https://cdn.zingchart.com/modules/";
ZC.LICENSE = ["569d52cefae586f634c54f86dc99e6a9", "ee6b7db5b51705a13dc2339db3edaf6d"];

var myConfig = {
    type: 'line',
    backgroundColor: '#2C2C39',
    title: {
        text: 'OASI - Stabio',
        adjustLayout: true,
        fontColor: "#E3E3E5",
        marginTop: 7
    },
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
        minValue: oasi_min_value,
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
        format:"%v m3/s"
    },
    "scale-y-2": {
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
        }
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
            fontColor: "#2C2C39",
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
        text: "Deflusso",
        values: oasi_values,
        scales: "scale-x, scale-y",
        lineColor: '#E34247',
        marker: {
            backgroundColor: '#E34247'
        }
    }, {
        values: [165.57, 170.47, 197.17, 164.64, 132.73, 176.89, 139.41, 158.71, 177.85, 138.87, 135.74, 167.06, 156.42, 182, 169.73, 151.08, 165.58, 146.29, 124.5, 181.71, 143.96, null, null, null, 146, 172.6, 149.81, 161.09, 175.88, 149.39, 184.1, 123.85, 186.82, 139.72, 138.61, 170.28, 164.06, 184.33, null, null, 131.85, 133.32, 134.49, 143.79, 125.23],
        scales: "scale-x, scale-y-2",
        lineColor: '#FEB32E',
        marker: {
            backgroundColor: '#FEB32E'
        }
    }, /*{
        values: [70.19, 96.56, 75.04, 51.58, 82.8, 68.14, 89.61, null, 45.33, 98.59, 92.9, 66.94, null, 74.08, 57.25, 79.68, 89.66, 64.56, 96.59, 79.96, 98.08, 42.93, 91.93, 56.23, 82.66, null, 85.76, 74.98, 51, 66.99, 63.02, 63.8, 44.33, 77.56, 95.28, 60.93, 59.6, 80.58, 68.51, 67.63, 69.76, 40.54, 78.42, 90.4, 82.3],
        lineColor: '#31A59A',
        marker: {
            backgroundColor: '#31A59A'
        }
    }*/
    ]
};

zingchart.render({
    id: 'water_chart',
    data: myConfig,
    height: '500',
    width: '100%'
});

zingchart.shape_click = function (p) {
    if (p.shapeid == "view_all") {
        zingchart.exec(p.id, 'viewall');
    }
}
