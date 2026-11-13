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

  const BASE_FONT = 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif';
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
          speed: 380
        }
      },
      dataLabels: { enabled: false },
      stroke: { curve: 'smooth', width: type === 'bar' ? 0 : 2.5 },
      grid: {
        borderColor: '#F1F5F9',
        strokeDashArray: 3,
        padding: { left: 6, right: 8, top: 4, bottom: 0 }
      },
      xaxis: {
        axisBorder: { show: false },
        axisTicks: { show: false },
        labels: { style: { colors: '#64748B', fontSize: '11.5px' } }
      },
      yaxis: {
        labels: { style: { colors: '#64748B', fontSize: '11.5px' } }
      },
      legend: {
        position: 'top',
        horizontalAlign: 'right',
        fontSize: '12px',
        markers: { radius: 3, width: 9, height: 9 }
      },
      tooltip: { theme: 'dark' }
    };
  }

  const CHART_REGISTRY = {
    /* ==================== SUPER ADMIN CHARTS ==================== */
    'sa-revenue-trend': {
      build: (range) => {
        const map = {
          '12M': {
            cats: ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
            sub:  [24200, 26100, 27400, 28900, 30200, 31500, 33800, 35400, 41200, 43900, 46100, 48920],
            rech: [11400, 12800, 13100, 14600, 15200, 14900, 16800, 18100, 22400, 24100, 25800, 27640]
          },
          '90D': {
            cats: ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8', 'Wk 9', 'Wk 10', 'Wk 11', 'Wk 12'],
            sub:  [9800, 10200, 10400, 11100, 10900, 11500, 11800, 12100, 12000, 12400, 12700, 13200],
            rech: [5200, 5400, 5900, 6100, 6000, 6350, 6500, 6800, 6700, 7100, 7250, 7540]
          },
          '30D': {
            cats: ['Nov 1', 'Nov 4', 'Nov 7', 'Nov 10', 'Nov 13', 'Nov 16', 'Nov 19', 'Nov 22', 'Nov 25', 'Nov 28'],
            sub:  [3900, 4200, 4150, 4680, 4520, 4890, 5100, 5040, 5380, 5620],
            rech: [2100, 2340, 2280, 2610, 2590, 2740, 2880, 2910, 3100, 3290]
          }
        };
        const d = map[range] || map['12M'];
        return Object.assign(baseChartOptions('area', 285), {
          colors: [PALETTE.indigo, PALETTE.emerald],
          series: [
            { name: 'Subscription Revenue', data: d.sub },
            { name: 'Recharge Volume', data: d.rech }
          ],
          fill: {
            type: 'gradient',
            gradient: { shadeIntensity: 1, opacityFrom: 0.24, opacityTo: 0.02, stops: [0, 95, 100] }
          },
          xaxis: { categories: d.cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } },
          yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px' }, formatter: (v) => '$' + (v / 1000).toFixed(1) + 'k' } },
          tooltip: { y: { formatter: (v) => '$' + Number(v).toLocaleString('en-US') + '.00' } }
        });
      }
    },

    'sa-school-growth': {
      build: () => Object.assign(baseChartOptions('line', 265), {
        colors: [PALETTE.indigo, PALETTE.teal],
        series: [
          { name: 'Total Registered Schools', data: [28, 31, 34, 36, 39, 41, 44, 46, 48, 50, 51, 52] },
          { name: 'Active Boarding Campuses', data: [26, 29, 32, 34, 37, 39, 42, 44, 46, 48, 49, 50] }
        ],
        xaxis: { categories: ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
      })
    },

    'sa-call-usage-trend': {
      build: (range) => {
        const d = range === '7D'
          ? { cats: ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue'], mins: [7820, 8140, 9420, 12680, 14120, 8390, 8940], calls: [910, 945, 1120, 1480, 1620, 980, 1040] }
          : { cats: ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8'], mins: [52400, 54800, 56100, 58900, 61200, 59800, 63400, 66850], calls: [6120, 6380, 6510, 6890, 7120, 6940, 7410, 7820] };
        return Object.assign(baseChartOptions('line', 265), {
          colors: [PALETTE.indigo, PALETTE.sky],
          series: [
            { name: 'Calling Minutes', data: d.mins },
            { name: 'Completed Sessions', data: d.calls }
          ],
          xaxis: { categories: d.cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
        });
      }
    },

    'sa-subscription-donut': {
      build: () => ({
        chart: { type: 'donut', height: 260, fontFamily: BASE_FONT },
        colors: [PALETTE.indigo, PALETTE.emerald, PALETTE.amber, PALETTE.rose],
        labels: ['Enterprise Annual (24)', 'Campus Growth (19)', 'Standard Quarterly (7)', 'Expired / Suspended (2)'],
        series: [24, 19, 7, 2],
        stroke: { width: 2, colors: ['#FFFFFF'] },
        dataLabels: { enabled: false },
        plotOptions: { pie: { donut: { size: '70%', labels: { show: true, total: { show: true, label: 'Total Schools', fontSize: '12px', color: '#64748B', formatter: () => '52' } } } } },
        legend: { position: 'bottom', fontSize: '11.5px' },
        tooltip: { theme: 'dark' }
      })
    },

    'sa-student-status-donut': {
      build: () => ({
        chart: { type: 'donut', height: 260, fontFamily: BASE_FONT },
        colors: [PALETTE.emerald, PALETTE.amber, PALETTE.muted],
        labels: ['Active Accounts (17,210)', 'Expiring <14d (680)', 'Inactive / Expired (540)'],
        series: [17210, 680, 540],
        stroke: { width: 2, colors: ['#FFFFFF'] },
        dataLabels: { enabled: false },
        plotOptions: { pie: { donut: { size: '70%', labels: { show: true, total: { show: true, label: 'Students', fontSize: '12px', color: '#64748B', formatter: () => '18,430' } } } } },
        legend: { position: 'bottom', fontSize: '11.5px' },
        tooltip: { theme: 'dark' }
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
      build: () => Object.assign(baseChartOptions('area', 275), {
        colors: [PALETTE.indigo, PALETTE.teal],
        series: [
          { name: 'Gross Territory Revenue', data: [10200, 11400, 10900, 12300, 12800, 13400, 14900, 15800, 16200, 17400, 18100, 19450] },
          { name: 'Net Partner Commission (18%)', data: [1836, 2052, 1962, 2214, 2304, 2412, 2682, 2844, 2916, 3132, 3258, 3501] }
        ],
        fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.22, opacityTo: 0.02 } },
        xaxis: { categories: ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } },
        yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px' }, formatter: (v) => '$' + (v / 1000).toFixed(1) + 'k' } },
        tooltip: { y: { formatter: (v) => '$' + Number(v).toLocaleString('en-US') } }
      })
    },

    'fr-commission-bar': {
      build: () => Object.assign(baseChartOptions('bar', 265), {
        colors: [PALETTE.teal, PALETTE.amber],
        plotOptions: { bar: { borderRadius: 4, columnWidth: '50%' } },
        series: [
          { name: 'Settled Commission', data: [2210, 2390, 2580, 2740, 2910, 3258] },
          { name: 'Pending Settlement', data: [0, 0, 0, 0, 180, 3420] }
        ],
        xaxis: { categories: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } },
        tooltip: { y: { formatter: (v) => '$' + Number(v).toLocaleString('en-US') } }
      })
    },

    'fr-school-students-donut': {
      build: () => ({
        chart: { type: 'donut', height: 265, fontFamily: BASE_FONT },
        colors: [PALETTE.indigo, PALETTE.teal, PALETTE.sky, PALETTE.amber, PALETTE.muted],
        labels: ['Oakridge Academy (684)', 'Westfield Hostel (512)', 'St. Jude Institute (430)', 'Silverstone Prep (295)', '14 Other Campuses (4,499)'],
        series: [684, 512, 430, 295, 4499],
        stroke: { width: 2, colors: ['#FFFFFF'] },
        dataLabels: { enabled: false },
        plotOptions: { pie: { donut: { size: '68%', labels: { show: true, total: { show: true, label: 'Assigned Students', fontSize: '11.5px', formatter: () => '6,420' } } } } },
        legend: { position: 'bottom', fontSize: '11px' },
        tooltip: { theme: 'dark' }
      })
    },

    'fr-calling-usage-line': {
      build: () => Object.assign(baseChartOptions('line', 255), {
        colors: [PALETTE.indigo],
        series: [{ name: 'Territory Calling Minutes', data: [18400, 19200, 21500, 20900, 23400, 24800, 26120, 27940] }],
        xaxis: { categories: ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
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
      build: () => Object.assign(baseChartOptions('area', 270), {
        colors: [PALETTE.indigo, PALETTE.emerald],
        series: [
          { name: 'Completed Calls', data: [118, 124, 131, 196, 218, 129, 142] },
          { name: 'Restricted / Outside Window', data: [6, 4, 8, 3, 2, 7, 5] }
        ],
        fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.22, opacityTo: 0.02 } },
        xaxis: { categories: ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Today'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
      })
    },

    'sch-weekly-duration': {
      build: () => Object.assign(baseChartOptions('bar', 270), {
        colors: [PALETTE.sky],
        plotOptions: { bar: { borderRadius: 5, columnWidth: '48%' } },
        series: [{ name: 'Minutes Used', data: [1240, 1380, 1510, 2340, 2690, 1420, 1595] }],
        xaxis: { categories: ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Today'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } },
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
      build: () => ({
        chart: { type: 'donut', height: 260, fontFamily: BASE_FONT },
        colors: [PALETTE.emerald, PALETTE.amber, PALETTE.rose],
        labels: ['Active Accounts (644)', 'Expiring Soon (14)', 'Inactive / Expired (26)'],
        series: [644, 14, 26],
        stroke: { width: 2, colors: ['#FFFFFF'] },
        dataLabels: { enabled: false },
        plotOptions: { pie: { donut: { size: '70%', labels: { show: true, total: { show: true, label: 'Oakridge Total', fontSize: '11.5px', formatter: () => '684' } } } } },
        legend: { position: 'bottom', fontSize: '11.5px' },
        tooltip: { theme: 'dark' }
      })
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
      build: () => Object.assign(baseChartOptions('line', 260), {
        colors: [PALETTE.emerald, PALETTE.indigo],
        series: [
          { name: 'Parent Portal Top-Ups', data: [38, 44, 52, 94, 61, 68] },
          { name: 'School Desk Allocations', data: [14, 12, 18, 42, 19, 23] }
        ],
        xaxis: { categories: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'], axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
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
