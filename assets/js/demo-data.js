/* ==========================================================================
   Source 2 Destination — Ephemeral In-Memory Demonstration Dataset
   File: assets/js/demo-data.js
   ==========================================================================
   IMPORTANT:
   - Strictly temporary in-memory JavaScript data for UI demonstration.
   - Resets completely on browser refresh (no browser storage APIs used).
   - All institutions, individuals, phone numbers, and IDs are 100% fictional.
   ========================================================================== */

(function (window) {
  'use strict';

  const S2D_DEMO = {
    currentContext: {
      superAdmin: {
        name: 'Eleanor Vance',
        fullName: 'Eleanor Vance',
        initials: 'EV',
        email: 'e.vance@source2destination.io',
        roleLabel: 'Super Administrator',
        organization: 'Source 2 Destination Global HQ'
      },
      franchise: {
        id: 'FRN-101',
        name: 'Marcus Sterling',
        fullName: 'Marcus Sterling',
        initials: 'MS',
        email: 'm.sterling@northeast-edunet.com',
        roleLabel: 'Franchise Partner',
        franchiseName: 'North-East EduNet Partners',
        commissionRate: 18.0,
        territory: 'Northeast Boarding Corridor'
      },
      schoolAdmin: {
        id: 'SCH-1001',
        name: 'Dr. Arthur Pendelton',
        fullName: 'Dr. Arthur Pendelton',
        initials: 'AP',
        email: 'admin@oakridge-academy.edu',
        roleLabel: 'School Administrator',
        schoolName: 'Oakridge Residential Academy',
        franchiseName: 'North-East EduNet Partners'
      }
    },

    franchises: [
      { id: 'FRN-101', name: 'North-East EduNet Partners', director: 'Marcus Sterling', email: 'm.sterling@northeast-edunet.com', phone: '+1 (555) 201-4400', territory: 'Northeast Corridor', schoolsCount: 18, studentsCount: 6420, commissionRate: '18%', revenue: 148920.00, earnedCommission: 26805.60, pendingCommission: 3420.00, status: 'Active' },
      { id: 'FRN-102', name: 'Pacific Crest Scholastic Group', director: 'Claire Lin', email: 'c.lin@pacificscholastic.org', phone: '+1 (555) 309-8821', territory: 'West Coast & Pacific', schoolsCount: 14, studentsCount: 5180, commissionRate: '16%', revenue: 119400.00, earnedCommission: 19104.00, pendingCommission: 2150.00, status: 'Active' },
      { id: 'FRN-103', name: 'Heartland Boarding Solutions', director: 'Gregory Caldwell', email: 'g.caldwell@heartlandboarding.com', phone: '+1 (555) 418-7732', territory: 'Midwest Campus Network', schoolsCount: 11, studentsCount: 3890, commissionRate: '15%', revenue: 88450.00, earnedCommission: 13267.50, pendingCommission: 1680.00, status: 'Active' },
      { id: 'FRN-104', name: 'Atlantic Campus Connect', director: 'Sophia Mercer', email: 's.mercer@atlanticcampus.io', phone: '+1 (555) 612-9014', territory: 'South Atlantic Region', schoolsCount: 9, studentsCount: 2940, commissionRate: '15%', revenue: 64200.00, earnedCommission: 9630.00, pendingCommission: 940.00, status: 'Active' }
    ],

    schools: [
      { id: 'SCH-1001', code: 'OAK-01', name: 'Oakridge Residential Academy', city: 'Hartford, CT', franchiseId: 'FRN-101', franchise: 'North-East EduNet Partners', adminName: 'Dr. Arthur Pendelton', adminEmail: 'admin@oakridge-academy.edu', phone: '+1 (555) 210-9001', students: 684, activeStudents: 658, devices: 28, callingMinutes: 42850, subscriptionPlan: 'Enterprise Boarding Annual', subscriptionStatus: 'Active', renewalDate: '2027-08-15', status: 'Active', createdDate: '2025-06-12' },
      { id: 'SCH-1002', code: 'WST-02', name: 'Westfield Collegiate Hostel', city: 'Boston, MA', franchiseId: 'FRN-101', franchise: 'North-East EduNet Partners', adminName: 'Hannah Abbott', adminEmail: 'h.abbott@westfieldhostel.edu', phone: '+1 (555) 210-9044', students: 512, activeStudents: 494, devices: 22, callingMinutes: 31420, subscriptionPlan: 'Campus Growth Annual', subscriptionStatus: 'Active', renewalDate: '2027-05-30', status: 'Active', createdDate: '2025-08-03' },
      { id: 'SCH-1003', code: 'STJ-03', name: 'St. Jude Boarding Institute', city: 'Providence, RI', franchiseId: 'FRN-101', franchise: 'North-East EduNet Partners', adminName: 'Father Thomas Keaton', adminEmail: 't.keaton@stjudeboarding.org', phone: '+1 (555) 219-3310', students: 430, activeStudents: 405, devices: 18, callingMinutes: 25900, subscriptionPlan: 'Campus Growth Annual', subscriptionStatus: 'Expiring', renewalDate: '2026-11-24', status: 'Active', createdDate: '2025-11-24' },
      { id: 'SCH-1004', code: 'GRN-04', name: 'Greenwood International Prep', city: 'Seattle, WA', franchiseId: 'FRN-102', franchise: 'Pacific Crest Scholastic Group', adminName: 'Victoria Chen', adminEmail: 'v.chen@greenwoodprep.edu', phone: '+1 (555) 334-1120', students: 790, activeStudents: 771, devices: 34, callingMinutes: 51200, subscriptionPlan: 'Enterprise Boarding Annual', subscriptionStatus: 'Active', renewalDate: '2027-09-01', status: 'Active', createdDate: '2025-09-01' },
      { id: 'SCH-1005', code: 'CRS-05', name: 'Crestview Boys & Girls Hostel', city: 'Portland, OR', franchiseId: 'FRN-102', franchise: 'Pacific Crest Scholastic Group', adminName: 'Daniel Ross', adminEmail: 'd.ross@crestviewhostel.org', phone: '+1 (555) 398-4412', students: 345, activeStudents: 318, devices: 14, callingMinutes: 18740, subscriptionPlan: 'Standard Hostel Quarterly', subscriptionStatus: 'Active', renewalDate: '2027-01-15', status: 'Active', createdDate: '2026-01-15' },
      { id: 'SCH-1006', code: 'MPL-06', name: 'Maplewood Residential High', city: 'Madison, WI', franchiseId: 'FRN-103', franchise: 'Heartland Boarding Solutions', adminName: 'Rebecca Thornton', adminEmail: 'r.thornton@maplewoodhigh.edu', phone: '+1 (555) 482-6601', students: 468, activeStudents: 440, devices: 19, callingMinutes: 27310, subscriptionPlan: 'Campus Growth Annual', subscriptionStatus: 'Expiring', renewalDate: '2026-11-19', status: 'Active', createdDate: '2025-11-19' },
      { id: 'SCH-1007', code: 'SLV-07', name: 'Silverstone Preparatory Campus', city: 'Albany, NY', franchiseId: 'FRN-101', franchise: 'North-East EduNet Partners', adminName: 'Julian Vance-Hall', adminEmail: 'j.hall@silverstoneprep.edu', phone: '+1 (555) 289-7741', students: 295, activeStudents: 0, devices: 12, callingMinutes: 6120, subscriptionPlan: 'Standard Hostel Quarterly', subscriptionStatus: 'Expired', renewalDate: '2026-10-15', status: 'Suspended', createdDate: '2025-10-15' },
      { id: 'SCH-1008', code: 'HRB-08', name: 'Harborview Collegiate Academy', city: 'Charleston, SC', franchiseId: 'FRN-104', franchise: 'Atlantic Campus Connect', adminName: 'Miriam Brooks', adminEmail: 'm.brooks@harborview.edu', phone: '+1 (555) 640-5590', students: 540, activeStudents: 526, devices: 24, callingMinutes: 34890, subscriptionPlan: 'Enterprise Boarding Annual', subscriptionStatus: 'Active', renewalDate: '2027-06-30', status: 'Active', createdDate: '2026-06-30' }
    ],

    schoolAdmins: [
      { id: 'ADM-201', name: 'Dr. Arthur Pendelton', email: 'admin@oakridge-academy.edu', phone: '+1 (555) 210-9001', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', designation: 'Principal & Primary Admin', mfaEnabled: 'Enabled', lastLogin: '2026-11-10 08:42', status: 'Active' },
      { id: 'ADM-202', name: 'Clarissa Sterling', email: 'c.sterling@oakridge-academy.edu', phone: '+1 (555) 210-9015', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', designation: 'Hostel Operations Coordinator', mfaEnabled: 'Enabled', lastLogin: '2026-11-10 07:55', status: 'Active' },
      { id: 'ADM-203', name: 'Hannah Abbott', email: 'h.abbott@westfieldhostel.edu', phone: '+1 (555) 210-9044', schoolId: 'SCH-1002', school: 'Westfield Collegiate Hostel', designation: 'Director of Student Welfare', mfaEnabled: 'Enabled', lastLogin: '2026-11-09 19:14', status: 'Active' },
      { id: 'ADM-204', name: 'Father Thomas Keaton', email: 't.keaton@stjudeboarding.org', phone: '+1 (555) 219-3310', schoolId: 'SCH-1003', school: 'St. Jude Boarding Institute', designation: 'Campus Rector', mfaEnabled: 'Pending', lastLogin: '2026-11-09 16:30', status: 'Active' },
      { id: 'ADM-205', name: 'Victoria Chen', email: 'v.chen@greenwoodprep.edu', phone: '+1 (555) 334-1120', schoolId: 'SCH-1004', school: 'Greenwood International Prep', designation: 'Dean of Residential Life', mfaEnabled: 'Enabled', lastLogin: '2026-11-10 09:05', status: 'Active' },
      { id: 'ADM-206', name: 'Daniel Ross', email: 'd.ross@crestviewhostel.org', phone: '+1 (555) 398-4412', schoolId: 'SCH-1005', school: 'Crestview Boys & Girls Hostel', designation: 'Senior Administrator', mfaEnabled: 'Enabled', lastLogin: '2026-11-08 14:22', status: 'Active' },
      { id: 'ADM-207', name: 'Rebecca Thornton', email: 'r.thornton@maplewoodhigh.edu', phone: '+1 (555) 482-6601', schoolId: 'SCH-1006', school: 'Maplewood Residential High', designation: 'Operations Admin', mfaEnabled: 'Enabled', lastLogin: '2026-11-10 08:11', status: 'Active' },
      { id: 'ADM-208', name: 'Julian Vance-Hall', email: 'j.hall@silverstoneprep.edu', phone: '+1 (555) 289-7741', schoolId: 'SCH-1007', school: 'Silverstone Preparatory Campus', designation: 'Campus Administrator', mfaEnabled: 'Disabled', lastLogin: '2026-10-14 11:08', status: 'Inactive' }
    ],

    students: [
      { id: 'STU-4001', studentCode: 'S2D-OAK-8841', name: 'Liam Hawthorne', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', franchiseId: 'FRN-101', className: 'Grade 10', section: 'Section A', hostelWing: 'North Hall · Rm 204', guardianName: 'Robert Hawthorne', guardianRelation: 'Father', primaryPhone: '+1 (555) 801-2210', secondaryPhone: '+1 (555) 801-2211', remainingMinutes: 142, dailyLimitMin: 15, validityStart: '2026-08-01', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7701 (North Hall Booth 1)', status: 'Active', addedDate: '2026-08-01' },
      { id: 'STU-4002', studentCode: 'S2D-OAK-8842', name: 'Clara Bennett', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', franchiseId: 'FRN-101', className: 'Grade 9', section: 'Section B', hostelWing: 'East Gables · Rm 112', guardianName: 'Margaret Bennett', guardianRelation: 'Mother', primaryPhone: '+1 (555) 802-3490', secondaryPhone: '+1 (555) 802-3499', remainingMinutes: 98, dailyLimitMin: 15, validityStart: '2026-08-01', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7702 (East Gables Booth 1)', status: 'Active', addedDate: '2026-08-02' },
      { id: 'STU-4003', studentCode: 'S2D-OAK-8843', name: 'Noah Montgomery', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', franchiseId: 'FRN-101', className: 'Grade 11', section: 'Section A', hostelWing: 'North Hall · Rm 308', guardianName: 'David Montgomery', guardianRelation: 'Father', primaryPhone: '+1 (555) 803-5120', secondaryPhone: '+1 (555) 803-5125', remainingMinutes: 18, dailyLimitMin: 12, validityStart: '2026-05-15', validityExpiry: '2026-11-18', validityStatus: 'Expiring', assignedDevice: 'DEV-7701 (North Hall Booth 1)', status: 'Active', addedDate: '2026-05-15' },
      { id: 'STU-4004', studentCode: 'S2D-OAK-8844', name: 'Amelia Fletcher', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', franchiseId: 'FRN-101', className: 'Grade 12', section: 'Section C', hostelWing: 'East Gables · Rm 305', guardianName: 'Evelyn Fletcher', guardianRelation: 'Mother', primaryPhone: '+1 (555) 804-7740', secondaryPhone: '+1 (555) 804-7741', remainingMinutes: 215, dailyLimitMin: 20, validityStart: '2026-08-10', validityExpiry: '2027-06-15', validityStatus: 'Active', assignedDevice: 'DEV-7703 (East Gables Booth 2)', status: 'Active', addedDate: '2026-08-10' },
      { id: 'STU-4005', studentCode: 'S2D-OAK-8845', name: 'Oliver Kingsley', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', franchiseId: 'FRN-101', className: 'Grade 8', section: 'Section A', hostelWing: 'Junior Wing · Rm 105', guardianName: 'Henry Kingsley', guardianRelation: 'Father', primaryPhone: '+1 (555) 805-1192', secondaryPhone: '+1 (555) 805-1198', remainingMinutes: 0, dailyLimitMin: 10, validityStart: '2026-04-01', validityExpiry: '2026-10-31', validityStatus: 'Expired', assignedDevice: 'DEV-7704 (Junior Wing Kiosk)', status: 'Inactive', addedDate: '2026-04-01' },
      { id: 'STU-4006', studentCode: 'S2D-OAK-8846', name: 'Sophia Whitaker', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', franchiseId: 'FRN-101', className: 'Grade 10', section: 'Section B', hostelWing: 'East Gables · Rm 214', guardianName: 'Catherine Whitaker', guardianRelation: 'Legal Guardian', primaryPhone: '+1 (555) 806-6631', secondaryPhone: '+1 (555) 806-6639', remainingMinutes: 64, dailyLimitMin: 15, validityStart: '2026-06-01', validityExpiry: '2026-11-22', validityStatus: 'Expiring', assignedDevice: 'DEV-7702 (East Gables Booth 1)', status: 'Active', addedDate: '2026-06-01' },
      { id: 'STU-4007', studentCode: 'S2D-WST-5510', name: 'Ethan Gallagher', schoolId: 'SCH-1002', school: 'Westfield Collegiate Hostel', franchiseId: 'FRN-101', className: 'Grade 11', section: 'Section A', hostelWing: 'Beacon Block · Rm 402', guardianName: 'Patrick Gallagher', guardianRelation: 'Father', primaryPhone: '+1 (555) 811-4402', secondaryPhone: '+1 (555) 811-4409', remainingMinutes: 175, dailyLimitMin: 15, validityStart: '2026-08-15', validityExpiry: '2027-05-30', validityStatus: 'Active', assignedDevice: 'DEV-7705 (Beacon Kiosk A)', status: 'Active', addedDate: '2026-08-15' },
      { id: 'STU-4008', studentCode: 'S2D-WST-5511', name: 'Maya Sullivan', schoolId: 'SCH-1002', school: 'Westfield Collegiate Hostel', franchiseId: 'FRN-101', className: 'Grade 9', section: 'Section C', hostelWing: 'Harbor Wing · Rm 118', guardianName: 'Laura Sullivan', guardianRelation: 'Mother', primaryPhone: '+1 (555) 812-9087', secondaryPhone: '+1 (555) 812-9088', remainingMinutes: 112, dailyLimitMin: 15, validityStart: '2026-08-15', validityExpiry: '2027-05-30', validityStatus: 'Active', assignedDevice: 'DEV-7706 (Harbor Kiosk B)', status: 'Active', addedDate: '2026-08-16' },
      { id: 'STU-4009', studentCode: 'S2D-STJ-3301', name: 'Lucas Pritchard', schoolId: 'SCH-1003', school: 'St. Jude Boarding Institute', franchiseId: 'FRN-101', className: 'Grade 12', section: 'Section A', hostelWing: 'St. Bede Hall · Rm 201', guardianName: 'Alan Pritchard', guardianRelation: 'Father', primaryPhone: '+1 (555) 820-3100', secondaryPhone: '+1 (555) 820-3105', remainingMinutes: 28, dailyLimitMin: 12, validityStart: '2026-05-20', validityExpiry: '2026-11-20', validityStatus: 'Expiring', assignedDevice: 'DEV-7707 (St. Bede Kiosk 1)', status: 'Active', addedDate: '2026-05-20' },
      { id: 'STU-4010', studentCode: 'S2D-GRN-9104', name: 'Chloe Takahashi', schoolId: 'SCH-1004', school: 'Greenwood International Prep', franchiseId: 'FRN-102', className: 'Grade 10', section: 'Section A', hostelWing: 'Cascade Dorm · Rm 310', guardianName: 'Kenji Takahashi', guardianRelation: 'Father', primaryPhone: '+1 (555) 831-7022', secondaryPhone: '+1 (555) 831-7023', remainingMinutes: 240, dailyLimitMin: 20, validityStart: '2026-09-01', validityExpiry: '2027-06-30', validityStatus: 'Active', assignedDevice: 'DEV-7708 (Cascade Booth 1)', status: 'Active', addedDate: '2026-09-01' },
      { id: 'STU-4011', studentCode: 'S2D-OAK-8847', name: 'Benjamin Mercer', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', franchiseId: 'FRN-101', className: 'Grade 7', section: 'Section B', hostelWing: 'Junior Wing · Rm 112', guardianName: 'Iris Mercer', guardianRelation: 'Mother', primaryPhone: '+1 (555) 807-4501', secondaryPhone: '+1 (555) 807-4502', remainingMinutes: 130, dailyLimitMin: 10, validityStart: '2026-08-20', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7704 (Junior Wing Kiosk)', status: 'Active', addedDate: '2026-08-20' },
      { id: 'STU-4012', studentCode: 'S2D-OAK-8848', name: 'Grace Kensington', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', franchiseId: 'FRN-101', className: 'Grade 11', section: 'Section B', hostelWing: 'East Gables · Rm 310', guardianName: 'Philip Kensington', guardianRelation: 'Father', primaryPhone: '+1 (555) 808-9920', secondaryPhone: '+1 (555) 808-9921', remainingMinutes: 0, dailyLimitMin: 15, validityStart: '2026-08-01', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'Unassigned', status: 'Inactive', addedDate: '2026-08-05' }
    ],

    classes: [
      { id: 'CLS-07', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', className: 'Grade 7', supervisor: 'Mrs. Nadine Wallace', sectionsCount: 3, studentsCount: 92, activeAccounts: 89, defaultDailyMinutes: 10, scheduleGroup: 'Junior Evening Window', status: 'Active' },
      { id: 'CLS-08', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', className: 'Grade 8', supervisor: 'Mr. Leonard Grant', sectionsCount: 3, studentsCount: 104, activeAccounts: 98, defaultDailyMinutes: 10, scheduleGroup: 'Junior Evening Window', status: 'Active' },
      { id: 'CLS-09', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', className: 'Grade 9', supervisor: 'Ms. Rachel Donovan', sectionsCount: 4, studentsCount: 122, activeAccounts: 119, defaultDailyMinutes: 15, scheduleGroup: 'Standard Hostel Window', status: 'Active' },
      { id: 'CLS-10', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', className: 'Grade 10', supervisor: 'Mr. Victor Sterling', sectionsCount: 4, studentsCount: 128, activeAccounts: 125, defaultDailyMinutes: 15, scheduleGroup: 'Standard Hostel Window', status: 'Active' },
      { id: 'CLS-11', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', className: 'Grade 11', supervisor: 'Dr. Helena Price', sectionsCount: 3, studentsCount: 118, activeAccounts: 111, defaultDailyMinutes: 15, scheduleGroup: 'Senior Study-Safe Window', status: 'Active' },
      { id: 'CLS-12', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', className: 'Grade 12', supervisor: 'Prof. Malcolm Reed', sectionsCount: 3, studentsCount: 120, activeAccounts: 116, defaultDailyMinutes: 20, scheduleGroup: 'Senior Study-Safe Window', status: 'Active' }
    ],

    sections: [
      { id: 'SEC-10A', classId: 'CLS-10', className: 'Grade 10', sectionName: 'Section A', roomWing: 'North Hall · Floor 2', advisor: 'Mr. Victor Sterling', studentsCount: 34, activeCallers: 34, assignedBooth: 'North Hall Booth 1', status: 'Active' },
      { id: 'SEC-10B', classId: 'CLS-10', className: 'Grade 10', sectionName: 'Section B', roomWing: 'East Gables · Floor 2', advisor: 'Ms. Claire Sutton', studentsCount: 32, activeCallers: 31, assignedBooth: 'East Gables Booth 1', status: 'Active' },
      { id: 'SEC-09B', classId: 'CLS-09', className: 'Grade 9', sectionName: 'Section B', roomWing: 'East Gables · Floor 1', advisor: 'Ms. Rachel Donovan', studentsCount: 31, activeCallers: 30, assignedBooth: 'East Gables Booth 1', status: 'Active' },
      { id: 'SEC-11A', classId: 'CLS-11', className: 'Grade 11', sectionName: 'Section A', roomWing: 'North Hall · Floor 3', advisor: 'Dr. Helena Price', studentsCount: 39, activeCallers: 37, assignedBooth: 'North Hall Booth 2', status: 'Active' },
      { id: 'SEC-12C', classId: 'CLS-12', className: 'Grade 12', sectionName: 'Section C', roomWing: 'East Gables · Floor 3', advisor: 'Prof. Malcolm Reed', studentsCount: 40, activeCallers: 39, assignedBooth: 'East Gables Booth 2', status: 'Active' },
      { id: 'SEC-08A', classId: 'CLS-08', className: 'Grade 8', sectionName: 'Section A', roomWing: 'Junior Wing · Floor 1', advisor: 'Mr. Leonard Grant', studentsCount: 35, activeCallers: 32, assignedBooth: 'Junior Wing Kiosk', status: 'Active' }
    ],

    guardians: [
      { id: 'GRD-501', name: 'Robert Hawthorne', studentId: 'STU-4001', studentName: 'Liam Hawthorne', className: 'Grade 10 · Sec A', relation: 'Father', fatherPhone: '+1 (555) 801-2210', motherPhone: '+1 (555) 801-2211', emergencyPhone: '+1 (555) 801-2299', email: 'r.hawthorne@example.com', verification: 'KYC Verified', whitelistStatus: 'Authorized (2 Numbers)', status: 'Active' },
      { id: 'GRD-502', name: 'Margaret Bennett', studentId: 'STU-4002', studentName: 'Clara Bennett', className: 'Grade 9 · Sec B', relation: 'Mother', fatherPhone: '+1 (555) 802-3499', motherPhone: '+1 (555) 802-3490', emergencyPhone: '+1 (555) 802-3400', email: 'm.bennett@example.com', verification: 'KYC Verified', whitelistStatus: 'Authorized (2 Numbers)', status: 'Active' },
      { id: 'GRD-503', name: 'David Montgomery', studentId: 'STU-4003', studentName: 'Noah Montgomery', className: 'Grade 11 · Sec A', relation: 'Father', fatherPhone: '+1 (555) 803-5120', motherPhone: '+1 (555) 803-5125', emergencyPhone: 'None', email: 'd.montgomery@example.com', verification: 'KYC Verified', whitelistStatus: 'Authorized (2 Numbers)', status: 'Active' },
      { id: 'GRD-504', name: 'Evelyn Fletcher', studentId: 'STU-4004', studentName: 'Amelia Fletcher', className: 'Grade 12 · Sec C', relation: 'Mother', fatherPhone: '+1 (555) 804-7741', motherPhone: '+1 (555) 804-7740', emergencyPhone: '+1 (555) 804-7700', email: 'e.fletcher@example.com', verification: 'KYC Verified', whitelistStatus: 'Authorized (3 Numbers)', status: 'Active' },
      { id: 'GRD-505', name: 'Henry Kingsley', studentId: 'STU-4005', studentName: 'Oliver Kingsley', className: 'Grade 8 · Sec A', relation: 'Father', fatherPhone: '+1 (555) 805-1192', motherPhone: '+1 (555) 805-1198', emergencyPhone: 'None', email: 'h.kingsley@example.com', verification: 'Pending Renewal', whitelistStatus: 'Paused (Account Expired)', status: 'Inactive' },
      { id: 'GRD-506', name: 'Catherine Whitaker', studentId: 'STU-4006', studentName: 'Sophia Whitaker', className: 'Grade 10 · Sec B', relation: 'Legal Guardian', fatherPhone: 'N/A', motherPhone: 'N/A', emergencyPhone: '+1 (555) 806-6631', email: 'c.whitaker@example.com', verification: 'Court Letter Verified', whitelistStatus: 'Authorized (1 Number)', status: 'Active' }
    ],

    studentCodes: [
      { id: 'COD-701', code: 'S2D-OAK-8841', studentId: 'STU-4001', studentName: 'Liam Hawthorne', className: 'Grade 10 · Sec A', issuedBy: 'Backend Auth Engine', issuedAt: '2026-08-01 10:14', lastUsed: '2026-11-09 19:22', pinPolicy: 'Code + Biometric/Warden Unlock', status: 'Active' },
      { id: 'COD-702', code: 'S2D-OAK-8842', studentId: 'STU-4002', studentName: 'Clara Bennett', className: 'Grade 9 · Sec B', issuedBy: 'Backend Auth Engine', issuedAt: '2026-08-02 11:05', lastUsed: '2026-11-10 07:40', pinPolicy: 'Code + 4-Digit Student PIN', status: 'Active' },
      { id: 'COD-703', code: 'S2D-OAK-8843', studentId: 'STU-4003', studentName: 'Noah Montgomery', className: 'Grade 11 · Sec A', issuedBy: 'Backend Auth Engine', issuedAt: '2026-05-15 09:30', lastUsed: '2026-11-08 20:10', pinPolicy: 'Code + 4-Digit Student PIN', status: 'Active' },
      { id: 'COD-704', code: 'S2D-OAK-8844', studentId: 'STU-4004', studentName: 'Amelia Fletcher', className: 'Grade 12 · Sec C', issuedBy: 'Backend Auth Engine', issuedAt: '2026-08-10 14:18', lastUsed: '2026-11-09 20:45', pinPolicy: 'Code + 4-Digit Student PIN', status: 'Active' },
      { id: 'COD-705', code: 'S2D-OAK-8845', studentId: 'STU-4005', studentName: 'Oliver Kingsley', className: 'Grade 8 · Sec A', issuedBy: 'Backend Auth Engine', issuedAt: '2026-04-01 08:50', lastUsed: '2026-10-29 18:15', pinPolicy: 'Suspended (Validity Expired)', status: 'Suspended' },
      { id: 'COD-706', code: 'PENDING-SERVER-ISSUE', studentId: 'STU-4012', studentName: 'Grace Kensington', className: 'Grade 11 · Sec B', issuedBy: 'Awaiting DRF Issuance', issuedAt: '2026-11-09 16:00', lastUsed: 'Never', pinPolicy: 'Pending Activation', status: 'Pending' }
    ],

    rechargePlans: [
      { id: 'RPL-01', name: 'Starter Monthly Pack', price: 8.00, minutes: 90, validityDays: 30, perCallCap: '10 mins', applicability: 'All Schools', popular: false, status: 'Active' },
      { id: 'RPL-02', name: 'Standard Term Calling Pack', price: 22.00, minutes: 300, validityDays: 120, perCallCap: '15 mins', applicability: 'All Schools', popular: true, status: 'Active' },
      { id: 'RPL-03', name: 'Full Academic Year Pack', price: 54.00, minutes: 900, validityDays: 300, perCallCap: '15 mins', applicability: 'Boarding Schools', popular: true, status: 'Active' },
      { id: 'RPL-04', name: 'Senior Scholar Extended Pack', price: 68.00, minutes: 1200, validityDays: 300, perCallCap: '20 mins', applicability: 'Grades 11–12', popular: false, status: 'Active' },
      { id: 'RPL-05', name: 'Emergency Top-Up Booster', price: 5.00, minutes: 45, validityDays: 15, perCallCap: '10 mins', applicability: 'Warden / Admin Approved', popular: false, status: 'Active' }
    ],

    recharges: [
      { id: 'RCH-8001', date: '2026-11-10 08:30', studentId: 'STU-4001', studentName: 'Liam Hawthorne', studentCode: 'S2D-OAK-8841', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', planName: 'Standard Term Calling Pack', amount: 22.00, minutesAdded: 300, validityDays: 120, paymentMode: 'Parent Portal Card', status: 'Successful' },
      { id: 'RCH-8002', date: '2026-11-10 07:45', studentId: 'STU-4002', studentName: 'Clara Bennett', studentCode: 'S2D-OAK-8842', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', planName: 'Starter Monthly Pack', amount: 8.00, minutesAdded: 90, validityDays: 30, paymentMode: 'School Desk Credit', status: 'Successful' },
      { id: 'RCH-8003', date: '2026-11-09 18:12', studentId: 'STU-4007', studentName: 'Ethan Gallagher', studentCode: 'S2D-WST-5510', school: 'Westfield Collegiate Hostel', franchise: 'North-East EduNet Partners', planName: 'Full Academic Year Pack', amount: 54.00, minutesAdded: 900, validityDays: 300, paymentMode: 'ACH Transfer', status: 'Successful' },
      { id: 'RCH-8004', date: '2026-11-09 15:40', studentId: 'STU-4003', studentName: 'Noah Montgomery', studentCode: 'S2D-OAK-8843', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', planName: 'Standard Term Calling Pack', amount: 22.00, minutesAdded: 300, validityDays: 120, paymentMode: 'Franchise Bulk Wallet', status: 'Pending' },
      { id: 'RCH-8005', date: '2026-11-09 12:05', studentId: 'STU-4010', studentName: 'Chloe Takahashi', studentCode: 'S2D-GRN-9104', school: 'Greenwood International Prep', franchise: 'Pacific Crest Scholastic Group', planName: 'Senior Scholar Extended Pack', amount: 68.00, minutesAdded: 1200, validityDays: 300, paymentMode: 'Parent Portal Card', status: 'Successful' },
      { id: 'RCH-8006', date: '2026-11-08 17:20', studentId: 'STU-4005', studentName: 'Oliver Kingsley', studentCode: 'S2D-OAK-8845', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', planName: 'Starter Monthly Pack', amount: 8.00, minutesAdded: 90, validityDays: 30, paymentMode: 'Parent Portal Card', status: 'Failed' }
    ],

    subscriptions: [
      { id: 'SUB-9001', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', planName: 'Enterprise Boarding Annual', billingCycle: 'Annual', studentSeats: 750, deviceSeats: 35, amount: 8400.00, startDate: '2026-08-15', expiryDate: '2027-08-15', autoRenew: 'Enabled', status: 'Active' },
      { id: 'SUB-9002', schoolId: 'SCH-1002', school: 'Westfield Collegiate Hostel', franchise: 'North-East EduNet Partners', planName: 'Campus Growth Annual', billingCycle: 'Annual', studentSeats: 550, deviceSeats: 25, amount: 5900.00, startDate: '2026-05-30', expiryDate: '2027-05-30', autoRenew: 'Enabled', status: 'Active' },
      { id: 'SUB-9003', schoolId: 'SCH-1003', school: 'St. Jude Boarding Institute', franchise: 'North-East EduNet Partners', planName: 'Campus Growth Annual', billingCycle: 'Annual', studentSeats: 450, deviceSeats: 20, amount: 5900.00, startDate: '2025-11-24', expiryDate: '2026-11-24', autoRenew: 'Manual Invoice', status: 'Expiring' },
      { id: 'SUB-9004', schoolId: 'SCH-1004', school: 'Greenwood International Prep', franchise: 'Pacific Crest Scholastic Group', planName: 'Enterprise Boarding Annual', billingCycle: 'Annual', studentSeats: 850, deviceSeats: 40, amount: 8400.00, startDate: '2026-09-01', expiryDate: '2027-09-01', autoRenew: 'Enabled', status: 'Active' },
      { id: 'SUB-9005', schoolId: 'SCH-1006', school: 'Maplewood Residential High', franchise: 'Heartland Boarding Solutions', planName: 'Campus Growth Annual', billingCycle: 'Annual', studentSeats: 500, deviceSeats: 22, amount: 5900.00, startDate: '2025-11-19', expiryDate: '2026-11-19', autoRenew: 'Manual Invoice', status: 'Expiring' },
      { id: 'SUB-9006', schoolId: 'SCH-1007', school: 'Silverstone Preparatory Campus', franchise: 'North-East EduNet Partners', planName: 'Standard Hostel Quarterly', billingCycle: 'Quarterly', studentSeats: 300, deviceSeats: 15, amount: 1850.00, startDate: '2026-07-15', expiryDate: '2026-10-15', autoRenew: 'Disabled', status: 'Expired' }
    ],

    transactions: [
      { id: 'TXN-30001', date: '2026-11-10 08:30', entity: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', category: 'Student Recharge', reference: 'STRP-994821A', method: 'Visa •••• 4242', amount: 22.00, status: 'Successful' },
      { id: 'TXN-30002', date: '2026-11-09 19:05', entity: 'Greenwood International Prep', franchise: 'Pacific Crest Scholastic Group', category: 'Annual Subscription', reference: 'INV-2026-8840', method: 'Institutional Wire', amount: 8400.00, status: 'Successful' },
      { id: 'TXN-30003', date: '2026-11-09 15:40', entity: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', category: 'Bulk Credit Allocation', reference: 'ACH-773019B', method: 'ACH Bank Debit', amount: 1320.00, status: 'Pending' },
      { id: 'TXN-30004', date: '2026-11-09 11:20', entity: 'St. Jude Boarding Institute', franchise: 'North-East EduNet Partners', category: 'Subscription Renewal', reference: 'INV-2026-8832', method: 'Institutional Check', amount: 5900.00, status: 'Pending' },
      { id: 'TXN-30005', date: '2026-11-08 17:20', entity: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', category: 'Student Recharge', reference: 'STRP-994702F', method: 'Mastercard •••• 8119', amount: 8.00, status: 'Failed' },
      { id: 'TXN-30006', date: '2026-11-07 14:15', entity: 'Westfield Collegiate Hostel', franchise: 'North-East EduNet Partners', category: 'Duplicate Top-Up Reversal', reference: 'RFD-2026-0412', method: 'Visa •••• 1094', amount: 54.00, status: 'Refunded' },
      { id: 'TXN-30007', date: '2026-11-06 10:02', entity: 'Harborview Collegiate Academy', franchise: 'Atlantic Campus Connect', category: 'Annual Subscription', reference: 'INV-2026-8799', method: 'Institutional Wire', amount: 8400.00, status: 'Successful' }
    ],

    commissions: [
      { id: 'COM-5001', period: 'Nov 2026 (MTD)', school: 'Oakridge Residential Academy', sourceType: 'Recharges & Credits', grossAmount: 4820.00, rate: '18%', commissionEarned: 867.60, payoutDate: '2026-12-05', status: 'Pending' },
      { id: 'COM-5002', period: 'Nov 2026 (MTD)', school: 'Westfield Collegiate Hostel', sourceType: 'Recharges & Credits', grossAmount: 3190.00, rate: '18%', commissionEarned: 574.20, payoutDate: '2026-12-05', status: 'Pending' },
      { id: 'COM-5003', period: 'Oct 2026', school: 'Oakridge Residential Academy', sourceType: 'Subscription + Recharges', grossAmount: 14200.00, rate: '18%', commissionEarned: 2556.00, payoutDate: '2026-11-05', status: 'Successful' },
      { id: 'COM-5004', period: 'Oct 2026', school: 'Westfield Collegiate Hostel', sourceType: 'Recharges & Credits', grossAmount: 6450.00, rate: '18%', commissionEarned: 1161.00, payoutDate: '2026-11-05', status: 'Successful' },
      { id: 'COM-5005', period: 'Oct 2026', school: 'St. Jude Boarding Institute', sourceType: 'Recharges & Credits', grossAmount: 4120.00, rate: '18%', commissionEarned: 741.60, payoutDate: '2026-11-05', status: 'Successful' },
      { id: 'COM-5006', period: 'Sep 2026', school: 'Oakridge Residential Academy', sourceType: 'Annual Onboarding Bonus + Credits', grossAmount: 19800.00, rate: '18%', commissionEarned: 3564.00, payoutDate: '2026-10-05', status: 'Successful' }
    ],

    devices: [
      { id: 'DEV-7701', deviceName: 'North Hall Booth 1', serialNumber: 'S2D-TAB-90811A', imei: '358920104481901', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', wingLocation: 'North Hall · Floor 2', assignedMode: 'Shared Hostel Booth (34 Students)', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '2 mins ago', status: 'Active' },
      { id: 'DEV-7702', deviceName: 'East Gables Booth 1', serialNumber: 'S2D-TAB-90812B', imei: '358920104481902', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', wingLocation: 'East Gables · Floor 1', assignedMode: 'Shared Hostel Booth (61 Students)', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '1 min ago', status: 'Active' },
      { id: 'DEV-7703', deviceName: 'East Gables Booth 2', serialNumber: 'S2D-TAB-90813C', imei: '358920104481903', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', wingLocation: 'East Gables · Floor 3', assignedMode: 'Shared Hostel Booth (40 Students)', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '4 mins ago', status: 'Active' },
      { id: 'DEV-7704', deviceName: 'Junior Wing Kiosk', serialNumber: 'S2D-TAB-90814D', imei: '358920104481904', model: 'Lenovo Tab K11 Kiosk Edition', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', wingLocation: 'Junior Wing · Warden Desk', assignedMode: 'Warden-Supervised Kiosk', appVersion: 'v4.8.1-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Offline', lastHeartbeat: '3 hours ago', status: 'Active' },
      { id: 'DEV-7705', deviceName: 'Beacon Kiosk A', serialNumber: 'S2D-TAB-90821E', imei: '358920104482105', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1002', school: 'Westfield Collegiate Hostel', wingLocation: 'Beacon Block · Lobby', assignedMode: 'Shared Hostel Booth', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: 'Just now', status: 'Active' },
      { id: 'DEV-7706', deviceName: 'Harbor Kiosk B', serialNumber: 'S2D-TAB-90822F', imei: '358920104482106', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1002', school: 'Westfield Collegiate Hostel', wingLocation: 'Harbor Wing · Floor 1', assignedMode: 'Shared Hostel Booth', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '6 mins ago', status: 'Active' },
      { id: 'DEV-7707', deviceName: 'St. Bede Kiosk 1', serialNumber: 'S2D-TAB-90830G', imei: '358920104483007', model: 'Lenovo Tab K11 Kiosk Edition', schoolId: 'SCH-1003', school: 'St. Jude Boarding Institute', wingLocation: 'St. Bede Hall', assignedMode: 'Shared Hostel Booth', appVersion: 'v4.7.9-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Policy Update Pending', onlineStatus: 'Online', lastHeartbeat: '11 mins ago', status: 'Active' },
      { id: 'DEV-7708', deviceName: 'Cascade Booth 1', serialNumber: 'S2D-TAB-90841H', imei: '358920104484108', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1004', school: 'Greenwood International Prep', wingLocation: 'Cascade Dorm · Commons', assignedMode: 'Shared Hostel Booth', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '1 min ago', status: 'Active' },
      { id: 'DEV-7709', deviceName: 'Oakridge Spare Unit 05', serialNumber: 'S2D-TAB-90819J', imei: '358920104481909', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1001', school: 'Oakridge Residential Academy', wingLocation: 'IT Safe · Unassigned', assignedMode: 'Available Pool', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '18 mins ago', status: 'Available' },
      { id: 'DEV-7710', deviceName: 'Silverstone Terminal 01', serialNumber: 'S2D-TAB-90877K', imei: '358920104487710', model: 'Lenovo Tab K11 Kiosk Edition', schoolId: 'SCH-1007', school: 'Silverstone Preparatory Campus', wingLocation: 'Main Dormitory', assignedMode: 'Blocked (School Suspended)', appVersion: 'v4.7.5-kiosk', enrollmentStatus: 'Suspended', kioskCompliance: 'Non-Compliant (Tamper Alert)', onlineStatus: 'Offline', lastHeartbeat: '26 days ago', status: 'Blocked' }
    ],

    callHistory: [
      { id: 'CAL-99001', startTime: '2026-11-10 07:40', dateOnly: '2026-11-10', studentName: 'Clara Bennett', studentCode: 'S2D-OAK-8842', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', guardianName: 'Margaret Bennett (Mother)', authorizedNumber: '+1 (555) 802-3490', device: 'DEV-7702', duration: '08m 42s', minutesUsed: 9, remainingAfter: 98, disconnectReason: 'Normal Student Hangup', status: 'Completed' },
      { id: 'CAL-99002', startTime: '2026-11-09 20:45', dateOnly: '2026-11-09', studentName: 'Amelia Fletcher', studentCode: 'S2D-OAK-8844', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', guardianName: 'Evelyn Fletcher (Mother)', authorizedNumber: '+1 (555) 804-7740', device: 'DEV-7703', duration: '14m 58s', minutesUsed: 15, remainingAfter: 215, disconnectReason: 'Max Per-Call Cap Reached', status: 'Completed' },
      { id: 'CAL-99003', startTime: '2026-11-09 19:22', dateOnly: '2026-11-09', studentName: 'Liam Hawthorne', studentCode: 'S2D-OAK-8841', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', guardianName: 'Robert Hawthorne (Father)', authorizedNumber: '+1 (555) 801-2210', device: 'DEV-7701', duration: '11m 15s', minutesUsed: 12, remainingAfter: 142, disconnectReason: 'Normal Guardian Hangup', status: 'Completed' },
      { id: 'CAL-99004', startTime: '2026-11-09 19:05', dateOnly: '2026-11-09', studentName: 'Sophia Whitaker', studentCode: 'S2D-OAK-8846', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', guardianName: 'Catherine Whitaker (Guardian)', authorizedNumber: '+1 (555) 806-6631', device: 'DEV-7702', duration: '00m 00s', minutesUsed: 0, remainingAfter: 64, disconnectReason: 'No Answer at Destination', status: 'Missed' },
      { id: 'CAL-99005', startTime: '2026-11-09 18:50', dateOnly: '2026-11-09', studentName: 'Ethan Gallagher', studentCode: 'S2D-WST-5510', school: 'Westfield Collegiate Hostel', franchise: 'North-East EduNet Partners', guardianName: 'Patrick Gallagher (Father)', authorizedNumber: '+1 (555) 811-4402', device: 'DEV-7705', duration: '09m 30s', minutesUsed: 10, remainingAfter: 175, disconnectReason: 'Normal Hangup', status: 'Completed' },
      { id: 'CAL-99006', startTime: '2026-11-09 14:12', dateOnly: '2026-11-09', studentName: 'Noah Montgomery', studentCode: 'S2D-OAK-8843', school: 'Oakridge Residential Academy', franchise: 'North-East EduNet Partners', guardianName: 'David Montgomery (Father)', authorizedNumber: '+1 (555) 803-5120', device: 'DEV-7701', duration: '00m 00s', minutesUsed: 0, remainingAfter: 18, disconnectReason: 'Blocked: Academic Class Hours', status: 'Restricted' },
      { id: 'CAL-99007', startTime: '2026-11-08 20:18', dateOnly: '2026-11-08', studentName: 'Chloe Takahashi', studentCode: 'S2D-GRN-9104', school: 'Greenwood International Prep', franchise: 'Pacific Crest Scholastic Group', guardianName: 'Kenji Takahashi (Father)', authorizedNumber: '+1 (555) 831-7022', device: 'DEV-7708', duration: '16m 10s', minutesUsed: 17, remainingAfter: 240, disconnectReason: 'Normal Hangup', status: 'Completed' },
      { id: 'CAL-99008', startTime: '2026-11-08 19:40', dateOnly: '2026-11-08', studentName: 'Lucas Pritchard', studentCode: 'S2D-STJ-3301', school: 'St. Jude Boarding Institute', franchise: 'North-East EduNet Partners', guardianName: 'Alan Pritchard (Father)', authorizedNumber: '+1 (555) 820-3100', device: 'DEV-7707', duration: '07m 22s', minutesUsed: 8, remainingAfter: 28, disconnectReason: 'Normal Hangup', status: 'Completed' }
    ],

    wardens: [
      { id: 'WRD-601', name: 'Major Kenneth Cole (Ret.)', email: 'k.cole@oakridge-academy.edu', phone: '+1 (555) 210-9101', hostelWing: 'North Hall (Boys Grades 10–11)', shiftHours: '16:00 – 00:00', supervisedStudents: 185, supervisedDevices: 8, emergencyOverride: 'Authorized', status: 'Active' },
      { id: 'WRD-602', name: 'Matron Beatrice Holloway', email: 'b.holloway@oakridge-academy.edu', phone: '+1 (555) 210-9102', hostelWing: 'East Gables (Girls Grades 9–12)', shiftHours: '15:00 – 23:00', supervisedStudents: 240, supervisedDevices: 10, emergencyOverride: 'Authorized', status: 'Active' },
      { id: 'WRD-603', name: 'Mr. Simon Callahan', email: 's.callahan@oakridge-academy.edu', phone: '+1 (555) 210-9103', hostelWing: 'Junior Wing (Grades 7–8)', shiftHours: '15:30 – 22:00', supervisedStudents: 196, supervisedDevices: 6, emergencyOverride: 'Authorized', status: 'Active' },
      { id: 'WRD-604', name: 'Ms. Fiona Delgado', email: 'f.delgado@oakridge-academy.edu', phone: '+1 (555) 210-9104', hostelWing: 'All Wings · Night Relief', shiftHours: '23:00 – 07:00', supervisedStudents: 684, supervisedDevices: 28, emergencyOverride: 'Emergency Only', status: 'Active' },
      { id: 'WRD-605', name: 'Mr. Trevor Bates', email: 't.bates@oakridge-academy.edu', phone: '+1 (555) 210-9105', hostelWing: 'Sports Dormitory Annex', shiftHours: 'On Leave', supervisedStudents: 63, supervisedDevices: 4, emergencyOverride: 'Suspended', status: 'Inactive' }
    ],

    roles: [
      { id: 'ROL-01', name: 'Super Administrator', scope: 'Global Platform', usersCount: 3, description: 'Full governance across franchises, schools, billing, Android Enterprise policy, and IAM.', systemLocked: true, status: 'Active' },
      { id: 'ROL-02', name: 'Platform Finance Controller', scope: 'Global Finance', usersCount: 4, description: 'Manages subscriptions, gateway settlements, refunds, recharge plans, and franchise payouts.', systemLocked: false, status: 'Active' },
      { id: 'ROL-03', name: 'Franchise Partner Director', scope: 'Assigned Territory', usersCount: 14, description: 'Manages assigned schools, bulk student onboarding, credit allocations, and commission ledgers.', systemLocked: true, status: 'Active' },
      { id: 'ROL-04', name: 'School Principal / Primary Admin', scope: 'Single Campus', usersCount: 52, description: 'Full campus control over students, guardians, schedules, wardens, recharges, and booth devices.', systemLocked: true, status: 'Active' },
      { id: 'ROL-05', name: 'Hostel Chief Warden', scope: 'Hostel Wing', usersCount: 118, description: 'Supervises calling schedules, device booths, emergency call overrides, and call logs.', systemLocked: false, status: 'Active' },
      { id: 'ROL-06', name: 'Compliance & Audit Viewer', scope: 'Read-Only Global', usersCount: 2, description: 'Read-only inspection of call logs, guardian authorization trails, and security audit logs.', systemLocked: false, status: 'Active' }
    ],

    auditLogs: [
      { id: 'AUD-901', timestamp: '2026-11-10 08:44:12', actor: 'Eleanor Vance (Super Admin)', module: 'Calling Duration', action: 'Updated Global Max Per-Call Cap', target: 'Global Policy (20m ceiling)', ipAddress: '198.51.100.14', severity: 'Info' },
      { id: 'AUD-902', timestamp: '2026-11-10 08:15:04', actor: 'Dr. Arthur Pendelton (School Admin)', module: 'Guardian Whitelist', action: 'Verified Secondary Guardian Number', target: 'STU-4002 · Clara Bennett', ipAddress: '203.0.113.42', severity: 'Info' },
      { id: 'AUD-903', timestamp: '2026-11-09 21:10:39', actor: 'System Policy Engine', module: 'Device Compliance', action: 'Flagged Kiosk Policy Drift', target: 'DEV-7707 · St. Bede Kiosk 1', ipAddress: 'Internal Worker', severity: 'Warning' },
      { id: 'AUD-904', timestamp: '2026-11-09 16:02:51', actor: 'Marcus Sterling (Franchise)', module: 'Recharge Allocation', action: 'Submitted Bulk Credit Request', target: 'Oakridge Residential Academy ($1,320)', ipAddress: '192.0.2.88', severity: 'Info' },
      { id: 'AUD-905', timestamp: '2026-11-08 11:29:00', actor: 'Eleanor Vance (Super Admin)', module: 'School Status', action: 'Suspended Expired Campus Account', target: 'SCH-1007 · Silverstone Preparatory', ipAddress: '198.51.100.14', severity: 'Critical' }
    ],

    notifications: [
      { id: 'NTF-01', title: 'Subscription Renewal Due in 9 Days', desc: 'Maplewood Residential High (SCH-1006) expires on Nov 19, 2026.', time: '18 mins ago', category: 'Billing', unread: true },
      { id: 'NTF-02', title: '14 Student Validities Expiring Soon', desc: 'Oakridge & St. Jude campuses have student accounts expiring within 14 days.', time: '1 hour ago', category: 'Validity', unread: true },
      { id: 'NTF-03', title: 'Device Heartbeat Delayed', desc: 'DEV-7704 (Junior Wing Kiosk) has been offline for 3 hours.', time: '3 hours ago', category: 'Device', unread: false },
      { id: 'NTF-04', title: 'Monthly Commission Batch Ready', desc: 'November MTD ledger reconciled for 4 active franchises.', time: 'Yesterday', category: 'Finance', unread: false }
    ]
  };

  window.S2D_DEMO = S2D_DEMO;
})(window);
