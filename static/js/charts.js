/* ==========================================================================
   Source 2 Destination — Interactive Analytics & ApexCharts Engine
   File: assets/js/charts.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  const PALETTE = {
    indigo: '#0A2E52',      // S2D Brand Deep Navy (high contrast on white canvas)
    indigoLight: '#1E5288',
    indigoDark: '#02182D',
    crimson: '#DB2A22',     // S2D Signature Crimson Red
    emerald: '#10B981',
    amber: '#F59E0B',
    rose: '#DB2A22',        // Aligned with S2D Brand Crimson
    sky: '#0284C7',
    teal: '#0D9488',
    slate: '#64748B',
    muted: '#CBD5E1'
  };

  const BASE_FONT = "'Plus Jakarta Sans', 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
  const activeCharts = {};

  function baseChartOptions(type, height) {
    return {
      chart: {
        type,
        height: height || 265,
        fontFamily: BASE_FONT,
        toolbar: { show: false },
        zoom: { enabled: false },
        animations: {
          enabled: false
        }
      },
      dataLabels: { enabled: false },
      stroke: {
        curve: 'smooth', // Fluid, humanized organic curve
        width: type === 'bar' ? 0 : 3,
        lineCap: 'round'
      },
      markers: {
        size: 0,
        strokeWidth: 2,
        strokeColors: '#FFFFFF',
        hover: { size: 6 }
      },
      grid: {
        borderColor: '#F1F5F9',
        strokeDashArray: 3,
        padding: { left: 6, right: 8, top: 4, bottom: 0 }
      },
      xaxis: {
        axisBorder: { show: false },
        axisTicks: { show: false },
        crosshairs: {
          show: true,
          width: 1,
          opacity: 0.85,
          stroke: {
            color: '#DB2A22',
            width: 1,
            dashArray: 3
          }
        },
        labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } }
      },
      yaxis: {
        crosshairs: {
          show: true,
          position: 'back',
          stroke: {
            color: '#94A3B8',
            width: 1,
            dashArray: 3
          }
        },
        labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } }
      },
      legend: {
        position: 'top',
        horizontalAlign: 'right',
        fontSize: '12px',
        fontFamily: BASE_FONT,
        markers: { radius: 3, width: 9, height: 9 }
      },
      tooltip: {
        theme: 'dark',
        shared: true,
        intersect: false,
        style: { fontSize: '12px', fontFamily: BASE_FONT }
      }
    };
  }

  const CHART_REGISTRY = {
    /* ==================== SUPER ADMIN CHARTS ==================== */
    'sa-revenue-trend': {
      build: (range, viewType) => {
        const type = viewType || 'bar';
        const map = {
          '12M': {
            cats: ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
            sub:  [24200, 26100, 27800, 29900, 31400, 33500, 35800, 38400, 41200, 43900, 46100, 48920],
            rech: [11400, 12800, 13900, 15400, 16800, 18200, 19900, 21800, 23500, 25200, 26400, 27640]
          },
          '90D': {
            cats: ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8', 'Wk 9', 'Wk 10', 'Wk 11', 'Wk 12'],
            sub:  [9800, 10200, 10600, 11100, 11400, 11900, 12200, 12600, 12900, 13400, 13800, 14200],
            rech: [5200, 5600, 5900, 6300, 6600, 7000, 7300, 7700, 8000, 8400, 8800, 9200]
          },
          '30D': {
            cats: ['Nov 1', 'Nov 4', 'Nov 7', 'Nov 10', 'Nov 13', 'Nov 16', 'Nov 19', 'Nov 22', 'Nov 25', 'Nov 28'],
            sub:  [3900, 4150, 4380, 4620, 4850, 5100, 5320, 5580, 5840, 6100],
            rech: [2100, 2280, 2450, 2620, 2810, 3020, 3210, 3420, 3640, 3850]
          }
        };
        const d = map[range] || map['12M'];

        if (type === 'area') {
          return Object.assign(baseChartOptions('area', 285), {
            colors: [PALETTE.indigo, PALETTE.emerald],
            series: [
              { name: 'Subscription Revenue', data: d.sub },
              { name: 'Student Recharges', data: d.rech }
            ],
            fill: {
              type: 'gradient',
              gradient: { shadeIntensity: 1, opacityFrom: 0.35, opacityTo: 0.04, stops: [0, 92, 100] }
            },
            stroke: { curve: 'smooth', width: 3, lineCap: 'round' },
            markers: { size: 3.5, strokeWidth: 2, strokeColors: '#FFFFFF', hover: { size: 6 } },
            xaxis: { categories: d.cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
            yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT }, formatter: (v) => '₹' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) } },
            tooltip: { shared: true, intersect: false, y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
          });
        }

        // Substantial, balanced modern column view
        return Object.assign(baseChartOptions('bar', 285), {
          colors: [PALETTE.indigo, PALETTE.emerald],
          plotOptions: {
            bar: {
              horizontal: false,
              columnWidth: '46%',
              borderRadius: 6,
              borderRadiusApplication: 'end'
            }
          },
          series: [
            { name: 'Subscription Revenue', data: d.sub },
            { name: 'Student Recharges', data: d.rech }
          ],
          fill: {
            type: 'gradient',
            gradient: {
              shade: 'light',
              type: 'vertical',
              shadeIntensity: 0.15,
              opacityFrom: 0.98,
              opacityTo: 0.82,
              stops: [0, 90, 100]
            }
          },
          stroke: { show: true, width: 2, colors: ['transparent'] },
          xaxis: { categories: d.cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
          yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT }, formatter: (v) => '₹' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) } },
          tooltip: { shared: true, intersect: false, y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
        });
      }
    },

    'sa-school-growth': {
      build: () => Object.assign(baseChartOptions('line', 265), {
        colors: [PALETTE.indigo, PALETTE.teal],
        stroke: { curve: 'smooth', width: 3 },
        markers: { size: 4, strokeWidth: 2, strokeColors: '#FFFFFF' },
        series: [
          { name: 'Total Registered Schools', data: [28, 31, 34, 36, 39, 41, 44, 46, 48, 50, 51, 52] },
          { name: 'Active Boarding Campuses', data: [26, 29, 32, 34, 37, 39, 42, 44, 46, 48, 49, 50] }
        ],
        xaxis: { categories: ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
      })
    },

    'sa-call-usage-trend': {
      build: (range) => {
        const d = range === '7D'
          ? { cats: ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue'], mins: [7820, 8140, 9420, 12680, 14120, 8390, 8940], calls: [910, 945, 1120, 1480, 1620, 980, 1040] }
          : { cats: ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8'], mins: [52400, 54800, 56100, 58900, 61200, 59800, 63400, 66850], calls: [6120, 6380, 6510, 6890, 7120, 6940, 7410, 7820] };
        return Object.assign(baseChartOptions('bar', 265), {
          colors: [PALETTE.indigo, PALETTE.sky],
          plotOptions: { bar: { columnWidth: '46%', borderRadius: 5, borderRadiusApplication: 'end' } },
          series: [
            { name: 'Calling Minutes', data: d.mins },
            { name: 'Completed Sessions', data: d.calls }
          ],
          xaxis: { categories: d.cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
        });
      }
    },

    'sa-subscription-bar': {
      build: () => Object.assign(baseChartOptions('bar', 285), {
        colors: [PALETTE.indigo, PALETTE.teal, PALETTE.amber, PALETTE.rose],
        plotOptions: {
          bar: {
            borderRadius: 6,
            columnWidth: '48%',
            distributed: true
          }
        },
        series: [{
          name: 'Campuses Enrolled',
          data: [24, 19, 7, 2]
        }],
        xaxis: {
          categories: ['Enterprise Annual', 'Campus Growth', 'Standard Qtr', 'Suspended'],
          axisBorder: { show: false },
          axisTicks: { show: false },
          labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
        },
        legend: { show: false },
        tooltip: { y: { formatter: (v) => v + ' Schools' } }
      })
    },

    'sa-subscription-donut': {
      // Modern bar chart replacing oval donut
      build: () => Object.assign(baseChartOptions('bar', 285), {
        colors: [PALETTE.indigo, PALETTE.teal, PALETTE.amber, PALETTE.rose],
        plotOptions: {
          bar: {
            borderRadius: 6,
            columnWidth: '48%',
            distributed: true
          }
        },
        series: [{
          name: 'Campuses Enrolled',
          data: [24, 19, 7, 2]
        }],
        xaxis: {
          categories: ['Enterprise Annual', 'Campus Growth', 'Standard Qtr', 'Suspended'],
          axisBorder: { show: false },
          axisTicks: { show: false },
          labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
        },
        legend: { show: false },
        tooltip: { y: { formatter: (v) => v + ' Schools' } }
      })
    },

    'sa-student-status-donut': {
      // Modern bar chart replacing oval donut
      build: () => Object.assign(baseChartOptions('bar', 260), {
        colors: [PALETTE.emerald, PALETTE.amber, PALETTE.rose],
        plotOptions: {
          bar: {
            borderRadius: 6,
            columnWidth: '45%',
            distributed: true
          }
        },
        series: [{
          name: 'Student Accounts',
          data: [17210, 680, 540]
        }],
        xaxis: {
          categories: ['Active Accounts', 'Expiring <14d', 'Inactive / Expired'],
          axisBorder: { show: false },
          axisTicks: { show: false },
          labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
        },
        legend: { show: false },
        tooltip: { y: { formatter: (v) => Number(v).toLocaleString('en-IN') + ' Students' } }
      })
    },

    'sa-school-usage-bar': {
      build: () => Object.assign(baseChartOptions('bar', 275), {
        colors: [PALETTE.indigo],
        plotOptions: { bar: { borderRadius: 5, columnWidth: '48%', horizontal: false } },
        series: [{ name: 'Monthly Calling Minutes', data: [51200, 42850, 34890, 31420, 27310, 25900, 18740] }],
        xaxis: { categories: ['Greenwood', 'Oakridge', 'Harborview', 'Westfield', 'Maplewood', 'St. Jude', 'Crestview'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11px' } } },
        tooltip: { y: { formatter: (v) => Number(v).toLocaleString('en-US') + ' mins' } }
      })
    },

    'sa-payment-status-chart': {
      build: () => Object.assign(baseChartOptions('bar', 275), {
        colors: [PALETTE.emerald, PALETTE.amber, PALETTE.rose, PALETTE.sky],
        plotOptions: { bar: { borderRadius: 5, columnWidth: '46%', distributed: true } },
        series: [{ name: 'Transactions (30d)', data: [1284, 96, 31, 18] }],
        legend: { show: false },
        xaxis: { categories: ['Successful', 'Pending Settlement', 'Failed Auth', 'Refunded'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
      })
    },

    /* ==================== FRANCHISE CHARTS ==================== */
    'fr-revenue-chart': {
      build: (range, viewType) => {
        const dyn = (window.S2D_FRANCHISE_CHARTS && window.S2D_FRANCHISE_CHARTS.revenue) || null;
        const type = viewType || 'bar';
        const cats = dyn && dyn.categories && dyn.categories.length ? dyn.categories : ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'];
        const gross = dyn && dyn.gross && dyn.gross.length ? dyn.gross : [10200, 11100, 11900, 12800, 13600, 14500, 15400, 16200, 17100, 17900, 18800, 19450];
        const comm = dyn && dyn.commission && dyn.commission.length ? dyn.commission : [1836, 1998, 2142, 2304, 2448, 2610, 2772, 2916, 3078, 3222, 3384, 3501];

        if (type === 'area') {
          return Object.assign(baseChartOptions('area', 275), {
            colors: [PALETTE.indigo, PALETTE.teal],
            series: [
              { name: 'Gross Revenue', data: gross },
              { name: 'Commission (18%)', data: comm }
            ],
            fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.32, opacityTo: 0.04 } },
            stroke: { curve: 'smooth', width: 3, lineCap: 'round' },
            markers: { size: 3.5, strokeWidth: 2, strokeColors: '#FFFFFF', hover: { size: 6 } },
            xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
            yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT }, formatter: (v) => '₹' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) } },
            tooltip: { shared: true, intersect: false, y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
          });
        }

        return Object.assign(baseChartOptions('bar', 275), {
          colors: [PALETTE.indigo, PALETTE.teal],
          plotOptions: {
            bar: {
              horizontal: false,
              columnWidth: '46%',
              borderRadius: 6,
              borderRadiusApplication: 'end'
            }
          },
          series: [
            { name: 'Gross Revenue', data: gross },
            { name: 'Commission (18%)', data: comm }
          ],
          fill: {
            type: 'gradient',
            gradient: { shade: 'light', type: 'vertical', shadeIntensity: 0.15, opacityFrom: 0.98, opacityTo: 0.82, stops: [0, 90, 100] }
          },
          stroke: { show: true, width: 2, colors: ['transparent'] },
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
          yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT }, formatter: (v) => '₹' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) } },
          tooltip: { shared: true, intersect: false, y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
        });
      }
    },

    'fr-commission-bar': {
      build: () => {
        const dyn = (window.S2D_FRANCHISE_CHARTS && window.S2D_FRANCHISE_CHARTS.commissionBar) || null;
        const cats = dyn && dyn.categories && dyn.categories.length ? dyn.categories : ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'];
        const settled = dyn && dyn.settled && dyn.settled.length ? dyn.settled : [22100, 23900, 25800, 27400, 29100, 32580];
        const pending = dyn && dyn.pending && dyn.pending.length ? dyn.pending : [0, 0, 0, 0, 1800, 34200];
        return Object.assign(baseChartOptions('bar', 265), {
          colors: [PALETTE.teal, PALETTE.amber],
          plotOptions: { bar: { borderRadius: 4, columnWidth: '50%' } },
          series: [
            { name: 'Settled Commission', data: settled },
            { name: 'Pending Settlement', data: pending }
          ],
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } },
          tooltip: { y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
        });
      }
    },

    'fr-school-students-bar': {
      build: () => {
        const dyn = (window.S2D_FRANCHISE_CHARTS && window.S2D_FRANCHISE_CHARTS.schoolStudents) || null;
        const cats = dyn && dyn.categories && dyn.categories.length ? dyn.categories : ['Bishop Cotton', 'Doon Valley', 'Mayo Int.', 'Scindia', 'Sahyadri'];
        const data = dyn && dyn.data && dyn.data.length ? dyn.data : [790, 684, 512, 430, 345];
        return Object.assign(baseChartOptions('bar', 275), {
          colors: [PALETTE.indigo, PALETTE.teal, PALETTE.sky, PALETTE.amber, PALETTE.emerald],
          plotOptions: {
            bar: {
              borderRadius: 6,
              horizontal: true,
              barHeight: '56%',
              distributed: true
            }
          },
          series: [{
            name: 'Enrolled Boarders',
            data: data
          }],
          xaxis: {
            categories: cats,
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
          },
          legend: { show: false },
          tooltip: { y: { formatter: (v) => v + ' Students' } }
        });
      }
    },

    'fr-school-students-donut': {
      // Modern bar chart replacing oval donut
      build: () => {
        const dyn = (window.S2D_FRANCHISE_CHARTS && window.S2D_FRANCHISE_CHARTS.schoolStudents) || null;
        const cats = dyn && dyn.categories && dyn.categories.length ? dyn.categories : ['Bishop Cotton', 'Doon Valley', 'Mayo Int.', 'Scindia', 'Sahyadri'];
        const data = dyn && dyn.data && dyn.data.length ? dyn.data : [790, 684, 512, 430, 345];
        return Object.assign(baseChartOptions('bar', 275), {
          colors: [PALETTE.indigo, PALETTE.teal, PALETTE.sky, PALETTE.amber, PALETTE.emerald],
          plotOptions: {
            bar: {
              borderRadius: 6,
              horizontal: true,
              barHeight: '56%',
              distributed: true
            }
          },
          series: [{
            name: 'Enrolled Boarders',
            data: data
          }],
          xaxis: {
            categories: cats,
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
          },
          legend: { show: false },
          tooltip: { y: { formatter: (v) => v + ' Students' } }
        });
      }
    },

    'fr-calling-usage-line': {
      build: () => {
        const dyn = (window.S2D_FRANCHISE_CHARTS && window.S2D_FRANCHISE_CHARTS.callingUsage) || null;
        const cats = dyn && dyn.categories && dyn.categories.length ? dyn.categories : ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8'];
        const data = dyn && dyn.data && dyn.data.length ? dyn.data : [18400, 22100, 19500, 24800, 20900, 26400, 23120, 27940];
        return Object.assign(baseChartOptions('bar', 255), {
          colors: [PALETTE.indigo],
          plotOptions: { bar: { horizontal: false, columnWidth: '44%', borderRadius: 5, borderRadiusApplication: 'end' } },
          series: [{ name: 'Territory Calling Minutes', data: data }],
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
        });
      }
    },

    'fr-recharge-trend': {
      build: () => {
        const dyn = (window.S2D_FRANCHISE_CHARTS && window.S2D_FRANCHISE_CHARTS.rechargesTrend) || null;
        const cats = dyn && dyn.categories && dyn.categories.length ? dyn.categories : ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'];
        const data = dyn && dyn.data && dyn.data.length ? dyn.data : [142, 158, 165, 189, 204, 218, 246];
        return Object.assign(baseChartOptions('bar', 255), {
          colors: [PALETTE.emerald],
          plotOptions: { bar: { borderRadius: 5, columnWidth: '46%' } },
          series: [{ name: 'Completed Recharges', data: data }],
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
        });
      }
    },

    /* ==================== SCHOOL ADMIN CHARTS ==================== */
    'sch-daily-calls': {
      build: (range) => {
        // Strictly only bars per user requirement (no trend/area)
        const r = range || '30D';
        const live = window.S2D_SCHOOL_CHARTS && window.S2D_SCHOOL_CHARTS.dailyCalls;
        let cats = [];
        let completed = [];
        let restricted = [];

        if (live && live.ranges && live.ranges[r]) {
          cats = live.ranges[r].labels || [];
          completed = live.ranges[r].completed || [];
          restricted = live.ranges[r].restricted || [];
        } else if (live && Array.isArray(live.labels)) {
          cats = live.labels;
          completed = live.completed || [];
          restricted = live.restricted || [];
        } else {
          if (r === '12M') {
            cats = ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'];
            completed = [42, 48, 55, 62, 70, 78, 85, 92, 98, 105, 112, 120];
            restricted = [4, 5, 3, 6, 4, 7, 5, 8, 6, 7, 5, 6];
          } else if (r === '6M') {
            cats = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'];
            completed = [78, 85, 92, 98, 105, 120];
            restricted = [4, 7, 5, 8, 6, 6];
          } else {
            cats = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`);
            completed = Array.from({ length: 30 }, () => Math.floor(Math.random() * 18 + 5));
            restricted = Array.from({ length: 30 }, () => Math.floor(Math.random() * 3));
          }
        }

        const isDense = cats.length > 15;

        return Object.assign(baseChartOptions('bar', 270), {
          colors: [PALETTE.indigo, PALETTE.rose],
          plotOptions: {
            bar: {
              horizontal: false,
              columnWidth: isDense ? '58%' : '44%',
              borderRadius: isDense ? 3 : 6,
              borderRadiusApplication: 'end'
            }
          },
          series: [
            { name: 'Completed Calls', data: completed },
            { name: 'Blocked Calls', data: restricted }
          ],
          fill: {
            type: 'gradient',
            gradient: { shade: 'light', type: 'vertical', shadeIntensity: 0.15, opacityFrom: 0.98, opacityTo: 0.82, stops: [0, 90, 100] }
          },
          stroke: { show: true, width: isDense ? 1 : 2, colors: ['transparent'] },
          xaxis: {
            categories: cats,
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: {
              rotate: isDense ? -45 : 0,
              rotateAlways: false,
              hideOverlappingLabels: true,
              style: { colors: '#64748B', fontSize: isDense ? '10px' : '11.5px', fontFamily: BASE_FONT }
            }
          },
          tooltip: { shared: true, intersect: false, y: { formatter: (v) => v + ' Calls' } }
        });
      }
    },

    'sch-weekly-duration': {
      build: () => {
        const live = window.S2D_SCHOOL_CHARTS && window.S2D_SCHOOL_CHARTS.dailyCalls;
        const cats = (live && Array.isArray(live.labels)) ? live.labels : [];
        const completed = (live && Array.isArray(live.completed)) ? live.completed : [];
        return Object.assign(baseChartOptions('bar', 270), {
          colors: [PALETTE.sky],
          plotOptions: { bar: { horizontal: false, columnWidth: '44%', borderRadius: 5, borderRadiusApplication: 'end' } },
          series: [{ name: 'Completed Calls', data: completed }],
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
          tooltip: { y: { formatter: (v) => v + ' calls' } }
        });
      }
    },

    'sch-class-distribution': {
      build: () => {
        const live = window.S2D_SCHOOL_CHARTS && window.S2D_SCHOOL_CHARTS.classDistribution;
        const cats = (live && Array.isArray(live.labels)) ? live.labels : [];
        const activeData = (live && Array.isArray(live.active)) ? live.active : [];
        const inactiveData = (live && Array.isArray(live.inactive)) ? live.inactive : [];

        return Object.assign(baseChartOptions('bar', 260), {
          colors: [PALETTE.indigo, PALETTE.muted],
          chart: Object.assign(baseChartOptions('bar', 260).chart, { stacked: true }),
          plotOptions: { bar: { borderRadius: 4, columnWidth: '50%' } },
          series: [
            { name: 'Active Calling Accounts', data: activeData },
            { name: 'Inactive / Expired', data: inactiveData }
          ],
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
        });
      }
    },

    'sch-active-donut': {
      build: () => {
        const stats = window.S2D_SCHOOL_STATS || {};
        const active = stats.active_students || 0;
        const expiring = stats.expiring_count || 0;
        const inactive = stats.inactive_students || 0;
        return Object.assign(baseChartOptions('bar', 260), {
          colors: [PALETTE.emerald, PALETTE.amber, PALETTE.rose],
          plotOptions: {
            bar: {
              borderRadius: 6,
              columnWidth: '45%',
              distributed: true
            }
          },
          series: [{
            name: 'Student Accounts',
            data: [active, expiring, inactive]
          }],
          xaxis: {
            categories: ['Active Accounts', 'Expiring Soon', 'Inactive / Expired'],
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
          },
          legend: { show: false },
          tooltip: { y: { formatter: (v) => v + ' Students' } }
        });
      }
    },

    'sch-usage-by-class': {
      build: () => {
        const live = window.S2D_SCHOOL_CHARTS && window.S2D_SCHOOL_CHARTS.classUsage;
        const cats = (live && Array.isArray(live.labels)) ? live.labels : [];
        const mins = (live && Array.isArray(live.minutes)) ? live.minutes : [];

        return Object.assign(baseChartOptions('bar', 260), {
          colors: [PALETTE.teal],
          plotOptions: { bar: { borderRadius: 5, horizontal: true, barHeight: '55%' } },
          series: [{ name: 'Calling Minutes (30d)', data: mins }],
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
          tooltip: { y: { formatter: (v) => v + ' mins' } }
        });
      }
    },

    'sch-recharge-trend': {
      build: () => Object.assign(baseChartOptions('bar', 260), {
        colors: [PALETTE.emerald, PALETTE.indigo],
        plotOptions: { bar: { horizontal: false, columnWidth: '46%', borderRadius: 5, borderRadiusApplication: 'end' } },
        series: [
          { name: 'Parent Portal Top-Ups', data: [38, 44, 52, 94, 61, 68] },
          { name: 'School Desk Allocations', data: [14, 12, 18, 42, 19, 23] }
        ],
        xaxis: { categories: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
      })
    }
  };

  const chartState = {
    'sa-revenue-trend': { range: '12M', view: 'bar' },
    'fr-revenue-chart': { range: '12M', view: 'bar' },
    'sch-daily-calls': { range: '30D', view: 'bar' }
  };

  function updateTargetChart(key) {
    const entry = activeCharts[key];
    if (!entry || !entry.spec) return;
    const state = chartState[key] || { range: '12M', view: 'bar' };
    const updated = entry.spec.build(state.range, state.view);
    entry.instance.updateOptions(updated, true, true);
  }

  function mountCharts() {
    if (!window.ApexCharts) return;

    document.querySelectorAll('[data-s2d-chart]').forEach((el) => {
      const key = el.getAttribute('data-s2d-chart');
      const spec = CHART_REGISTRY[key];
      if (!spec) return;

      el.innerHTML = '';
      const state = chartState[key] || { range: '12M', view: 'bar' };
      const opts = spec.build(state.range, state.view);
      const chart = new window.ApexCharts(el, opts);
      chart.render();
      activeCharts[key] = { instance: chart, el, spec };
    });

    // Bind time-range switcher buttons
    document.querySelectorAll('[data-chart-target][data-range]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetKey = btn.getAttribute('data-chart-target');
        const range = btn.getAttribute('data-range');
        const group = btn.closest('.chart-range-group');
        if (group) {
          group.querySelectorAll('.chart-range-btn').forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
        }
        if (!chartState[targetKey]) chartState[targetKey] = { range: '12M', view: 'bar' };
        chartState[targetKey].range = range;
        updateTargetChart(targetKey);

        if (targetKey === 'sch-daily-calls') {
          const sub = document.getElementById('sch-daily-calls-subtitle');
          if (sub) {
            const desc = range === '30D' ? 'last 30 days' : (range === '6M' ? 'last 6 months' : 'last 12 months');
            sub.textContent = `Completed vs blocked calls over the ${desc}`;
          }
        }
      });
    });

    // Bind view-type switcher buttons (Bars vs Trend)
    document.querySelectorAll('[data-chart-target][data-view]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetKey = btn.getAttribute('data-chart-target');
        const view = btn.getAttribute('data-view');
        const group = btn.closest('.chart-range-group');
        if (group) {
          group.querySelectorAll('.chart-range-btn').forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
        }
        if (!chartState[targetKey]) chartState[targetKey] = { range: '12M', view: 'bar' };
        chartState[targetKey].view = view;
        updateTargetChart(targetKey);
      });
    });
  }

  window.S2DCharts = { mountCharts, activeCharts };
})(window, document);
