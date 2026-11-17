/* ==========================================================================
   Source 2 Destination — Interactive Analytics & ApexCharts Engine
   File: assets/js/charts.js
   ========================================================================== */

(function (window, document) {
  'use strict';

  const PALETTE = {
    indigo: '#4F46E5',
    indigoLight: '#818CF8',
    indigoDark: '#3730A3',
    emerald: '#10B981',
    amber: '#F59E0B',
    rose: '#EF4444',
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
          enabled: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
          easing: 'easeinout',
          speed: 400
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
            color: '#4F46E5',
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

  function spikeChartOptions(height) {
    return {
      chart: {
        type: 'bar',
        height: height || 275,
        fontFamily: BASE_FONT,
        toolbar: { show: false },
        zoom: { enabled: false },
        animations: {
          enabled: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
          easing: 'easeinout',
          speed: 400
        }
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: '18%', // Ultra-slender telemetric spike needles
          borderRadius: 4,
          borderRadiusApplication: 'end'
        }
      },
      dataLabels: { enabled: false },
      stroke: {
        show: true,
        width: 0,
        colors: ['transparent']
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: 'light',
          type: 'vertical',
          shadeIntensity: 0.25,
          opacityFrom: 0.96,
          opacityTo: 0.40,
          stops: [0, 85, 100]
        }
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
            color: '#4F46E5',
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
      build: (range) => {
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
        return Object.assign(spikeChartOptions(285), {
          colors: [PALETTE.indigo, PALETTE.emerald],
          series: [
            { name: 'Subscription Revenue Spikes', data: d.sub },
            { name: 'Recharge Volume Spikes', data: d.rech }
          ],
          xaxis: { categories: d.cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
          yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT }, formatter: (v) => '₹' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) } },
          tooltip: { y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
        });
      }
    },

    'sa-school-growth': {
      build: () => Object.assign(spikeChartOptions(265), {
        colors: [PALETTE.indigo, PALETTE.teal],
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
        return Object.assign(spikeChartOptions(265), {
          colors: [PALETTE.indigo, PALETTE.sky],
          series: [
            { name: 'Calling Minutes Spikes', data: d.mins },
            { name: 'Completed Sessions Spikes', data: d.calls }
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
      build: () => Object.assign(spikeChartOptions(275), {
        colors: [PALETTE.indigo, PALETTE.teal],
        series: [
          { name: 'Gross Territory Revenue Spikes', data: [10200, 11100, 11900, 12800, 13600, 14500, 15400, 16200, 17100, 17900, 18800, 19450] },
          { name: 'Net Partner Commission Spikes (18%)', data: [1836, 1998, 2142, 2304, 2448, 2610, 2772, 2916, 3078, 3222, 3384, 3501] }
        ],
        xaxis: { categories: ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
        yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT }, formatter: (v) => '₹' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) } },
        tooltip: { y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
      })
    },

    'fr-commission-bar': {
      build: () => Object.assign(baseChartOptions('bar', 265), {
        colors: [PALETTE.teal, PALETTE.amber],
        plotOptions: { bar: { borderRadius: 4, columnWidth: '50%' } },
        series: [
          { name: 'Settled Commission', data: [22100, 23900, 25800, 27400, 29100, 32580] },
          { name: 'Pending Settlement', data: [0, 0, 0, 0, 1800, 34200] }
        ],
        xaxis: { categories: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } },
        tooltip: { y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
      })
    },

    'fr-school-students-bar': {
      build: () => Object.assign(baseChartOptions('bar', 275), {
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
          data: [790, 684, 512, 430, 345]
        }],
        xaxis: {
          categories: ['Bishop Cotton', 'Doon Valley', 'Mayo Int.', 'Scindia', 'Sahyadri'],
          axisBorder: { show: false },
          axisTicks: { show: false },
          labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
        },
        legend: { show: false },
        tooltip: { y: { formatter: (v) => v + ' Students' } }
      })
    },

    'fr-school-students-donut': {
      // Modern bar chart replacing oval donut
      build: () => Object.assign(baseChartOptions('bar', 275), {
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
          data: [790, 684, 512, 430, 345]
        }],
        xaxis: {
          categories: ['Bishop Cotton', 'Doon Valley', 'Mayo Int.', 'Scindia', 'Sahyadri'],
          axisBorder: { show: false },
          axisTicks: { show: false },
          labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
        },
        legend: { show: false },
        tooltip: { y: { formatter: (v) => v + ' Students' } }
      })
    },

    'fr-calling-usage-line': {
      build: () => Object.assign(spikeChartOptions(255), {
        colors: [PALETTE.indigo],
        plotOptions: { bar: { horizontal: false, columnWidth: '14%', borderRadius: 4, borderRadiusApplication: 'end' } },
        series: [{ name: 'Territory Calling Minutes Spikes', data: [18400, 22100, 19500, 24800, 20900, 26400, 23120, 27940] }],
        xaxis: { categories: ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
      })
    },

    'fr-recharge-trend': {
      build: () => Object.assign(baseChartOptions('bar', 255), {
        colors: [PALETTE.emerald],
        plotOptions: { bar: { borderRadius: 5, columnWidth: '46%' } },
        series: [{ name: 'Completed Recharges', data: [142, 158, 165, 189, 204, 218, 246] }],
        xaxis: { categories: ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
      })
    },

    /* ==================== SCHOOL ADMIN CHARTS ==================== */
    'sch-daily-calls': {
      build: () => Object.assign(spikeChartOptions(270), {
        colors: [PALETTE.indigo, PALETTE.rose],
        series: [
          { name: 'Completed Calling Spikes', data: [118, 132, 145, 188, 212, 154, 168] },
          { name: 'Restricted / Blocked Spikes', data: [8, 6, 9, 14, 12, 7, 5] }
        ],
        xaxis: { categories: ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Today'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
        tooltip: { y: { formatter: (v) => v + ' Calls' } }
      })
    },

    'sch-weekly-duration': {
      build: () => Object.assign(spikeChartOptions(270), {
        colors: [PALETTE.sky],
        plotOptions: { bar: { horizontal: false, columnWidth: '16%', borderRadius: 4, borderRadiusApplication: 'end' } },
        series: [{ name: 'Minutes Used Spikes', data: [1240, 1380, 1510, 2340, 2690, 1420, 1595] }],
        xaxis: { categories: ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Today'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
        tooltip: { y: { formatter: (v) => v + ' mins' } }
      })
    },

    'sch-class-distribution': {
      build: () => Object.assign(baseChartOptions('bar', 260), {
        colors: [PALETTE.indigo, PALETTE.muted],
        chart: Object.assign(baseChartOptions('bar', 260).chart, { stacked: true }),
        plotOptions: { bar: { borderRadius: 4, columnWidth: '50%' } },
        series: [
          { name: 'Active Calling Accounts', data: [89, 98, 119, 125, 111, 116] },
          { name: 'Inactive / Expired', data: [3, 6, 3, 3, 7, 4] }
        ],
        xaxis: { categories: ['Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
      })
    },

    'sch-active-donut': {
      build: () => {
        const stats = window.S2D_SCHOOL_STATS || {};
        const active = stats.active_students !== undefined ? stats.active_students : 644;
        const expiring = stats.expiring_count !== undefined ? stats.expiring_count : 14;
        const inactive = stats.inactive_students !== undefined ? stats.inactive_students : 26;
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
      build: () => Object.assign(baseChartOptions('bar', 260), {
        colors: [PALETTE.teal],
        plotOptions: { bar: { borderRadius: 5, horizontal: true, barHeight: '55%' } },
        series: [{ name: 'Calling Minutes (30d)', data: [4820, 5390, 7410, 8620, 7890, 8720] }],
        xaxis: { categories: ['Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
      })
    },

    'sch-recharge-trend': {
      build: () => Object.assign(spikeChartOptions(260), {
        colors: [PALETTE.emerald, PALETTE.indigo],
        series: [
          { name: 'Parent Portal Top-Ups Spikes', data: [38, 44, 52, 94, 61, 68] },
          { name: 'School Desk Allocations Spikes', data: [14, 12, 18, 42, 19, 23] }
        ],
        xaxis: { categories: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
      })
    }
  };

  function mountCharts() {
    if (!window.ApexCharts) return;

    document.querySelectorAll('[data-s2d-chart]').forEach((el) => {
      const key = el.getAttribute('data-s2d-chart');
      const spec = CHART_REGISTRY[key];
      if (!spec) return;

      el.innerHTML = '';
      const opts = spec.build('12M');
      const chart = new window.ApexCharts(el, opts);
      chart.render();
      activeCharts[key] = { instance: chart, el, spec };
    });

    // Bind time-range switcher buttons [data-chart-target="sa-revenue-trend"][data-range="30D"]
    document.querySelectorAll('[data-chart-target]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetKey = btn.getAttribute('data-chart-target');
        const range = btn.getAttribute('data-range');
        const group = btn.closest('.chart-range-group');
        if (group) {
          group.querySelectorAll('.chart-range-btn').forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
        }
        const entry = activeCharts[targetKey];
        if (entry && entry.spec) {
          const updated = entry.spec.build(range);
          entry.instance.updateOptions(updated, true, true);
        }
      });
    });
  }

  window.S2DCharts = { mountCharts, activeCharts };
})(window, document);
