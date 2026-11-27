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
      noData: {
        text: 'No data available',
        align: 'center',
        verticalAlign: 'middle',
        style: {
          color: '#94A3B8',
          fontSize: '13px',
          fontFamily: BASE_FONT
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
        const dyn = (window.S2D_SUPERADMIN_CHARTS && window.S2D_SUPERADMIN_CHARTS.revenueTrend) || null;
        const type = viewType || 'bar';
        const cats = (dyn && Array.isArray(dyn.categories)) ? dyn.categories : [];
        const sub = (dyn && Array.isArray(dyn.subscriptions)) ? dyn.subscriptions : [];
        const rech = (dyn && Array.isArray(dyn.recharges)) ? dyn.recharges : [];
        const hasData = cats.length > 0 && (sub.some(v => v > 0) || rech.some(v => v > 0));

        if (!hasData) {
          return Object.assign(baseChartOptions(type, 285), {
            series: [{ name: '', data: [] }],
            xaxis: { categories: [] }
          });
        }

        if (type === 'area') {
          return Object.assign(baseChartOptions('area', 285), {
            colors: [PALETTE.indigo, PALETTE.emerald],
            series: [
              { name: 'Subscription Revenue', data: sub },
              { name: 'Student Recharges', data: rech }
            ],
            fill: {
              type: 'gradient',
              gradient: { shadeIntensity: 1, opacityFrom: 0.35, opacityTo: 0.04, stops: [0, 92, 100] }
            },
            stroke: { curve: 'smooth', width: 3, lineCap: 'round' },
            markers: { size: 3.5, strokeWidth: 2, strokeColors: '#FFFFFF', hover: { size: 6 } },
            xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
            yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT }, formatter: (v) => '₹' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) } },
            tooltip: { shared: true, intersect: false, y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
          });
        }

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
            { name: 'Subscription Revenue', data: sub },
            { name: 'Student Recharges', data: rech }
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
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } },
          yaxis: { labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT }, formatter: (v) => '₹' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v) } },
          tooltip: { shared: true, intersect: false, y: { formatter: (v) => '₹' + Number(v).toLocaleString('en-IN') } }
        });
      }
    },

    'sa-school-growth': {
      build: () => {
        const dyn = (window.S2D_SUPERADMIN_CHARTS && window.S2D_SUPERADMIN_CHARTS.schoolGrowth) || null;
        const cats = (dyn && Array.isArray(dyn.categories)) ? dyn.categories : [];
        const series = (dyn && Array.isArray(dyn.series)) ? dyn.series : [];
        if (!cats.length || !series.length) {
          return Object.assign(baseChartOptions('line', 265), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
        return Object.assign(baseChartOptions('line', 265), {
          colors: [PALETTE.indigo, PALETTE.teal],
          stroke: { curve: 'smooth', width: 3 },
          markers: { size: 4, strokeWidth: 2, strokeColors: '#FFFFFF' },
          series: series,
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
        });
      }
    },

    'sa-call-usage-trend': {
      build: () => {
        const dyn = (window.S2D_SUPERADMIN_CHARTS && window.S2D_SUPERADMIN_CHARTS.callUsage) || null;
        const cats = (dyn && Array.isArray(dyn.categories)) ? dyn.categories : [];
        const mins = (dyn && Array.isArray(dyn.mins)) ? dyn.mins : [];
        const calls = (dyn && Array.isArray(dyn.calls)) ? dyn.calls : [];
        if (!cats.length || !mins.length || !mins.some(v => v > 0)) {
          return Object.assign(baseChartOptions('bar', 265), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
        return Object.assign(baseChartOptions('bar', 265), {
          colors: [PALETTE.indigo, PALETTE.sky],
          plotOptions: { bar: { columnWidth: '46%', borderRadius: 5, borderRadiusApplication: 'end' } },
          series: [
            { name: 'Calling Minutes', data: mins },
            { name: 'Completed Sessions', data: calls }
          ],
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
        });
      }
    },

    'sa-subscription-bar': {
      build: () => {
        const dyn = (window.S2D_SUPERADMIN_CHARTS && window.S2D_SUPERADMIN_CHARTS.subscriptions) || null;
        const cats = (dyn && Array.isArray(dyn.categories)) ? dyn.categories : [];
        const data = (dyn && Array.isArray(dyn.data)) ? dyn.data : [];
        const hasData = data.some(v => v > 0);
        if (!hasData) {
          return Object.assign(baseChartOptions('bar', 285), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
        return Object.assign(baseChartOptions('bar', 285), {
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
            data: data
          }],
          xaxis: {
            categories: cats,
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
          },
          legend: { show: false },
          tooltip: { y: { formatter: (v) => v + ' Schools' } }
        });
      }
    },

    'sa-subscription-donut': {
      build: () => {
        const dyn = (window.S2D_SUPERADMIN_CHARTS && window.S2D_SUPERADMIN_CHARTS.subscriptions) || null;
        const cats = (dyn && Array.isArray(dyn.categories)) ? dyn.categories : [];
        const data = (dyn && Array.isArray(dyn.data)) ? dyn.data : [];
        const hasData = data.some(v => v > 0);
        if (!hasData) {
          return Object.assign(baseChartOptions('bar', 285), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
        return Object.assign(baseChartOptions('bar', 285), {
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
            data: data
          }],
          xaxis: {
            categories: cats,
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
          },
          legend: { show: false },
          tooltip: { y: { formatter: (v) => v + ' Schools' } }
        });
      }
    },

    'sa-student-status-donut': {
      build: () => {
        const dyn = (window.S2D_SUPERADMIN_CHARTS && window.S2D_SUPERADMIN_CHARTS.studentStatus) || null;
        const cats = (dyn && Array.isArray(dyn.categories)) ? dyn.categories : [];
        const data = (dyn && Array.isArray(dyn.data)) ? dyn.data : [];
        const hasData = data.some(v => v > 0);
        if (!hasData) {
          return Object.assign(baseChartOptions('bar', 260), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
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
            data: data
          }],
          xaxis: {
            categories: cats,
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: { style: { colors: '#64748B', fontSize: '11px', fontWeight: 500 } }
          },
          legend: { show: false },
          tooltip: { y: { formatter: (v) => Number(v).toLocaleString('en-IN') + ' Students' } }
        });
      }
    },

    'sa-school-usage-bar': {
      build: () => {
        const dyn = (window.S2D_SUPERADMIN_CHARTS && window.S2D_SUPERADMIN_CHARTS.schoolUsage) || null;
        const cats = (dyn && Array.isArray(dyn.categories)) ? dyn.categories : [];
        const data = (dyn && Array.isArray(dyn.data)) ? dyn.data : [];
        if (!cats.length || !data.length || !data.some(v => v > 0)) {
          return Object.assign(baseChartOptions('bar', 275), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
        return Object.assign(baseChartOptions('bar', 275), {
          colors: [PALETTE.indigo],
          plotOptions: { bar: { borderRadius: 5, columnWidth: '48%', horizontal: false } },
          series: [{ name: 'Monthly Calling Minutes', data: data }],
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11px' } } },
          tooltip: { y: { formatter: (v) => Number(v).toLocaleString('en-US') + ' mins' } }
        });
      }
    },

    'sa-payment-status-chart': {
      build: () => {
        const dyn = (window.S2D_SUPERADMIN_CHARTS && window.S2D_SUPERADMIN_CHARTS.paymentStatus) || null;
        const cats = (dyn && Array.isArray(dyn.categories)) ? dyn.categories : [];
        const data = (dyn && Array.isArray(dyn.data)) ? dyn.data : [];
        if (!cats.length || !data.length || !data.some(v => v > 0)) {
          return Object.assign(baseChartOptions('bar', 275), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
        return Object.assign(baseChartOptions('bar', 275), {
          colors: [PALETTE.emerald, PALETTE.amber, PALETTE.rose, PALETTE.sky],
          plotOptions: { bar: { borderRadius: 5, columnWidth: '46%', distributed: true } },
          series: [{ name: 'Transactions (30d)', data: data }],
          legend: { show: false },
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px' } } }
        });
      }
    },

    /* ==================== FRANCHISE CHARTS ==================== */
    'fr-revenue-chart': {
      build: (range, viewType) => {
        const dyn = (window.S2D_FRANCHISE_CHARTS && window.S2D_FRANCHISE_CHARTS.revenue) || null;
        const type = viewType || 'bar';
        const cats = dyn && Array.isArray(dyn.categories) ? dyn.categories : [];
        const gross = dyn && Array.isArray(dyn.gross) ? dyn.gross : [];
        const comm = dyn && Array.isArray(dyn.commission) ? dyn.commission : [];
        const hasData = cats.length > 0 && (gross.some(v => v > 0) || comm.some(v => v > 0));

        if (!hasData) {
          return Object.assign(baseChartOptions(type, 275), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }

        if (type === 'area') {
          return Object.assign(baseChartOptions('area', 275), {
            colors: [PALETTE.indigo, PALETTE.teal],
            series: [
              { name: 'Gross Revenue', data: gross },
              { name: 'Commission', data: comm }
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
            { name: 'Commission', data: comm }
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
        const cats = dyn && Array.isArray(dyn.categories) ? dyn.categories : [];
        const settled = dyn && Array.isArray(dyn.settled) ? dyn.settled : [];
        const pending = dyn && Array.isArray(dyn.pending) ? dyn.pending : [];
        const hasData = cats.length > 0 && (settled.some(v => v > 0) || pending.some(v => v > 0));
        if (!hasData) {
          return Object.assign(baseChartOptions('bar', 265), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
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
        const cats = dyn && Array.isArray(dyn.categories) ? dyn.categories : [];
        const data = dyn && Array.isArray(dyn.data) ? dyn.data : [];
        if (!cats.length || !data.length || !data.some(v => v > 0)) {
          return Object.assign(baseChartOptions('bar', 275), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
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
      build: () => {
        const dyn = (window.S2D_FRANCHISE_CHARTS && window.S2D_FRANCHISE_CHARTS.schoolStudents) || null;
        const cats = dyn && Array.isArray(dyn.categories) ? dyn.categories : [];
        const data = dyn && Array.isArray(dyn.data) ? dyn.data : [];
        if (!cats.length || !data.length || !data.some(v => v > 0)) {
          return Object.assign(baseChartOptions('bar', 275), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
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
        const cats = dyn && Array.isArray(dyn.categories) ? dyn.categories : [];
        const data = dyn && Array.isArray(dyn.data) ? dyn.data : [];
        if (!cats.length || !data.length || !data.some(v => v > 0)) {
          return Object.assign(baseChartOptions('bar', 255), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
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
        const cats = dyn && Array.isArray(dyn.categories) ? dyn.categories : [];
        const data = dyn && Array.isArray(dyn.data) ? dyn.data : [];
        if (!cats.length || !data.length || !data.some(v => v > 0)) {
          return Object.assign(baseChartOptions('bar', 255), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
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
        }

        const hasData = cats.length > 0 && (completed.some(v => v > 0) || restricted.some(v => v > 0));
        if (!hasData) {
          return Object.assign(baseChartOptions('bar', 270), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
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
        if (!cats.length || !completed.some(v => v > 0)) {
          return Object.assign(baseChartOptions('bar', 270), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
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
        const hasData = cats.length > 0 && (activeData.some(v => v > 0) || inactiveData.some(v => v > 0));
        if (!hasData) {
          return Object.assign(baseChartOptions('bar', 260), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }

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
        if (!active && !expiring && !inactive) {
          return Object.assign(baseChartOptions('bar', 260), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
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
        if (!cats.length || !mins.length || !mins.some(v => v > 0)) {
          return Object.assign(baseChartOptions('bar', 260), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
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
      build: () => {
        const live = window.S2D_SCHOOL_CHARTS && window.S2D_SCHOOL_CHARTS.rechargesTrend;
        const cats = (live && Array.isArray(live.categories)) ? live.categories : [];
        const parent = (live && Array.isArray(live.parent)) ? live.parent : [];
        const desk = (live && Array.isArray(live.desk)) ? live.desk : [];
        if (!cats.length || (!parent.some(v => v > 0) && !desk.some(v => v > 0))) {
          return Object.assign(baseChartOptions('bar', 260), { series: [{ name: '', data: [] }], xaxis: { categories: [] } });
        }
        return Object.assign(baseChartOptions('bar', 260), {
          colors: [PALETTE.emerald, PALETTE.indigo],
          plotOptions: { bar: { horizontal: false, columnWidth: '46%', borderRadius: 5, borderRadiusApplication: 'end' } },
          series: [
            { name: 'Parent Portal Top-Ups', data: parent },
            { name: 'School Desk Allocations', data: desk }
          ],
          xaxis: { categories: cats, axisBorder: { show: false }, axisTicks: { show: false }, labels: { style: { colors: '#64748B', fontSize: '11.5px', fontFamily: BASE_FONT } } }
        });
      }
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
    try {
      if (entry.instance) {
        if (!updated.series || updated.series.length === 0) {
          entry.instance.destroy();
          entry.el.innerHTML = '';
          const chart = new window.ApexCharts(entry.el, updated);
          chart.render();
          entry.instance = chart;
        } else {
          entry.instance.updateOptions(updated, true, true);
        }
      }
    } catch (e) {
      console.warn('Chart update handled:', e);
    }
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
