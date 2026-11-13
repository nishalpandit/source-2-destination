/* ==========================================================================
   Source 2 Destination — Ephemeral Demonstration Dataset (Indian Context)
   File: assets/js/demo-data.js
   ==========================================================================
   IMPORTANT:
   - In-memory demonstration dataset for UI fallback & demonstration.
   - All phone numbers use standard Indian format (+91).
   - All financial amounts use Indian Rupees (₹ / INR).
   ========================================================================== */

(function (window) {
  'use strict';

  const S2D_DEMO = {
    currentContext: {
      superAdmin: {
        name: 'Aarav Singhal',
        fullName: 'Aarav Singhal',
        initials: 'AS',
        email: 'aarav.singhal@source2destination.in',
        roleLabel: 'Super Administrator',
        organization: 'Source 2 Destination National HQ (New Delhi)'
      },
      franchise: {
        id: 'FRN-101',
        name: 'Vikramaditya Singhania',
        fullName: 'Vikramaditya Singhania',
        initials: 'VS',
        email: 'v.singhania@northedunet.in',
        roleLabel: 'Franchise Partner',
        franchiseName: 'North India EduNet Partners',
        commissionRate: 18.0,
        territory: 'North India Boarding Corridor'
      },
      schoolAdmin: {
        id: 'SCH-1001',
        name: 'Dr. Ramesh Chandra Sharma',
        fullName: 'Dr. Ramesh Chandra Sharma',
        initials: 'RS',
        email: 'principal@doonvalley.edu.in',
        roleLabel: 'School Administrator',
        schoolName: 'Doon Valley Residential Academy',
        franchiseName: 'North India EduNet Partners'
      }
    },

    franchises: [
      { id: 'FRN-101', name: 'North India EduNet Partners', director: 'Vikramaditya Singhania', email: 'v.singhania@northedunet.in', phone: '+91 98111 22334', territory: 'North India Boarding Corridor (Uttarakhand, HP, Punjab)', schoolsCount: 18, studentsCount: 6420, commissionRate: '18%', revenue: 1248920.00, earnedCommission: 224805.60, pendingCommission: 38420.00, status: 'Active' },
      { id: 'FRN-102', name: 'Western Scholastic Network', director: 'Sunita Deshmukh', email: 's.deshmukh@westernscholastic.in', phone: '+91 98220 33445', territory: 'Western Region (Maharashtra & Gujarat)', schoolsCount: 14, studentsCount: 5180, commissionRate: '16%', revenue: 984000.00, earnedCommission: 157440.00, pendingCommission: 24150.00, status: 'Active' },
      { id: 'FRN-103', name: 'Central Heartland Edutech', director: 'Rajeshwar Bundela', email: 'r.bundela@heartlandedutech.in', phone: '+91 98260 44556', territory: 'Central Region (Madhya Pradesh & Rajasthan)', schoolsCount: 11, studentsCount: 3890, commissionRate: '15%', revenue: 748500.00, earnedCommission: 112275.00, pendingCommission: 18680.00, status: 'Active' },
      { id: 'FRN-104', name: 'Southern Campus Connect', director: 'K. R. Meenakshi', email: 'kr.meenakshi@southerncampus.in', phone: '+91 98450 55667', territory: 'South India Network (Karnataka & Tamil Nadu)', schoolsCount: 9, studentsCount: 2940, commissionRate: '15%', revenue: 564200.00, earnedCommission: 84630.00, pendingCommission: 12940.00, status: 'Active' }
    ],

    schools: [
      { id: 'SCH-1001', code: 'DOON-01', name: 'Doon Valley Residential Academy', city: 'Dehradun, Uttarakhand', franchiseId: 'FRN-101', franchise: 'North India EduNet Partners', adminName: 'Dr. Ramesh Chandra Sharma', adminEmail: 'principal@doonvalley.edu.in', phone: '+91 98101 23456', students: 684, activeStudents: 658, devices: 28, callingMinutes: 42850, subscriptionPlan: 'Enterprise Boarding Annual', subscriptionStatus: 'Active', renewalDate: '2027-08-15', status: 'Active', createdDate: '2025-06-12' },
      { id: 'SCH-1002', code: 'MAYO-02', name: 'Mayo International Boarding School', city: 'Ajmer, Rajasthan', franchiseId: 'FRN-103', franchise: 'Central Heartland Edutech', adminName: 'Col. Devendra Rathore', adminEmail: 'admin@mayointernational.edu.in', phone: '+91 98290 34567', students: 512, activeStudents: 494, devices: 22, callingMinutes: 31420, subscriptionPlan: 'Campus Growth Annual', subscriptionStatus: 'Active', renewalDate: '2027-05-30', status: 'Active', createdDate: '2025-08-03' },
      { id: 'SCH-1003', code: 'SCN-03', name: 'Scindia Residential Campus', city: 'Gwalior, Madhya Pradesh', franchiseId: 'FRN-103', franchise: 'Central Heartland Edutech', adminName: 'Dr. Aniruddh Madhavrao', adminEmail: 'rector@scindiacampus.edu.in', phone: '+91 98260 56789', students: 430, activeStudents: 405, devices: 18, callingMinutes: 25900, subscriptionPlan: 'Campus Growth Annual', subscriptionStatus: 'Expiring', renewalDate: '2026-11-24', status: 'Active', createdDate: '2025-11-24' },
      { id: 'SCH-1004', code: 'BCP-04', name: 'Bishop Cotton Boys School & Hostel', city: 'Shimla, Himachal Pradesh', franchiseId: 'FRN-101', franchise: 'North India EduNet Partners', adminName: 'Rev. Joydeep Mukherjee', adminEmail: 'headmaster@bishopcottonshimla.edu.in', phone: '+91 98160 67890', students: 790, activeStudents: 771, devices: 34, callingMinutes: 51200, subscriptionPlan: 'Enterprise Boarding Annual', subscriptionStatus: 'Active', renewalDate: '2027-09-01', status: 'Active', createdDate: '2025-09-01' },
      { id: 'SCH-1005', code: 'SYH-05', name: 'Sahyadri International Residential School', city: 'Pune, Maharashtra', franchiseId: 'FRN-102', franchise: 'Western Scholastic Network', adminName: 'Dr. Sanjay Kulkarni', adminEmail: 's.kulkarni@sahyadriresidential.edu.in', phone: '+91 98230 78901', students: 345, activeStudents: 318, devices: 14, callingMinutes: 18740, subscriptionPlan: 'Standard Hostel Quarterly', subscriptionStatus: 'Active', renewalDate: '2027-01-15', status: 'Active', createdDate: '2026-01-15' }
    ],

    schoolAdmins: [
      { id: 'ADM-201', name: 'Dr. Ramesh Chandra Sharma', email: 'principal@doonvalley.edu.in', phone: '+91 98101 23456', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', designation: 'Principal & Primary Admin', mfaEnabled: 'Enabled', lastLogin: '2026-11-10 08:42', status: 'Active' },
      { id: 'ADM-202', name: 'Smt. Anjali Mehra', email: 'a.mehra@doonvalley.edu.in', phone: '+91 98101 23477', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', designation: 'Hostel Operations Coordinator', mfaEnabled: 'Enabled', lastLogin: '2026-11-10 07:55', status: 'Active' },
      { id: 'ADM-203', name: 'Col. Devendra Rathore', email: 'admin@mayointernational.edu.in', phone: '+91 98290 34567', schoolId: 'SCH-1002', school: 'Mayo International Boarding School', designation: 'Director of Student Welfare', mfaEnabled: 'Enabled', lastLogin: '2026-11-09 19:14', status: 'Active' },
      { id: 'ADM-204', name: 'Dr. Aniruddh Madhavrao', email: 'rector@scindiacampus.edu.in', phone: '+91 98260 56789', schoolId: 'SCH-1003', school: 'Scindia Residential Campus', designation: 'Campus Rector', mfaEnabled: 'Pending', lastLogin: '2026-11-09 16:30', status: 'Active' },
      { id: 'ADM-205', name: 'Rev. Joydeep Mukherjee', email: 'headmaster@bishopcottonshimla.edu.in', phone: '+91 98160 67890', schoolId: 'SCH-1004', school: 'Bishop Cotton Boys School & Hostel', designation: 'Dean of Residential Life', mfaEnabled: 'Enabled', lastLogin: '2026-11-10 09:05', status: 'Active' },
      { id: 'ADM-206', name: 'Dr. Sanjay Kulkarni', email: 's.kulkarni@sahyadriresidential.edu.in', phone: '+91 98230 78901', schoolId: 'SCH-1005', school: 'Sahyadri International Residential School', designation: 'Senior Administrator', mfaEnabled: 'Enabled', lastLogin: '2026-11-08 14:22', status: 'Active' }
    ],

    students: [
      { id: 'STU-4001', studentCode: 'S2D-DOON-8801', name: 'Aarav Sharma', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 10', section: 'Section A', hostelWing: 'Tagore Bhavan · Rm 204', guardianName: 'Rajesh Sharma', guardianRelation: 'Father', primaryPhone: '+91 98101 23456', secondaryPhone: '+91 98101 23457', remainingMinutes: 180, dailyLimitMin: 15, validityStart: '2026-08-01', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7701 (Tagore Bhavan Booth 1)', status: 'Active', addedDate: '2026-08-01' },
      { id: 'STU-4002', studentCode: 'S2D-DOON-8802', name: 'Ananya Iyer', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 9', section: 'Section B', hostelWing: 'Sarojini Sadan · Rm 112', guardianName: 'Meenakshi Iyer', guardianRelation: 'Mother', primaryPhone: '+91 98450 34567', secondaryPhone: '+91 98450 34568', remainingMinutes: 120, dailyLimitMin: 15, validityStart: '2026-08-01', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7702 (Sarojini Sadan Booth 1)', status: 'Active', addedDate: '2026-08-02' },
      { id: 'STU-4003', studentCode: 'S2D-DOON-8803', name: 'Vihaan Patel', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 11', section: 'Section A', hostelWing: 'Tagore Bhavan · Rm 308', guardianName: 'Sunil Patel', guardianRelation: 'Father', primaryPhone: '+91 98250 45678', secondaryPhone: '+91 98250 45679', remainingMinutes: 24, dailyLimitMin: 12, validityStart: '2026-05-15', validityExpiry: '2026-11-20', validityStatus: 'Expiring', assignedDevice: 'DEV-7701 (Tagore Bhavan Booth 1)', status: 'Active', addedDate: '2026-05-15' },
      { id: 'STU-4004', studentCode: 'S2D-DOON-8804', name: 'Diya Sen', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 12', section: 'Section C', hostelWing: 'Sarojini Sadan · Rm 305', guardianName: 'Sunita Sen', guardianRelation: 'Mother', primaryPhone: '+91 98300 56789', secondaryPhone: '+91 98300 56790', remainingMinutes: 215, dailyLimitMin: 20, validityStart: '2026-08-10', validityExpiry: '2027-06-15', validityStatus: 'Active', assignedDevice: 'DEV-7703 (Sarojini Sadan Booth 2)', status: 'Active', addedDate: '2026-08-10' },
      { id: 'STU-4005', studentCode: 'S2D-DOON-8805', name: 'Aditya Verma', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 8', section: 'Section A', hostelWing: 'Junior Wing · Rm 105', guardianName: 'Vikram Verma', guardianRelation: 'Father', primaryPhone: '+91 98110 67890', secondaryPhone: '+91 98110 67891', remainingMinutes: 0, dailyLimitMin: 10, validityStart: '2026-04-01', validityExpiry: '2026-10-31', validityStatus: 'Expired', assignedDevice: 'DEV-7704 (Junior Wing Kiosk)', status: 'Inactive', addedDate: '2026-04-01' },
      { id: 'STU-4006', studentCode: 'S2D-DOON-8806', name: 'Tanvi Deshmukh', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 10', section: 'Section B', hostelWing: 'Sarojini Sadan · Rm 214', guardianName: 'Ashok Deshmukh', guardianRelation: 'Father', primaryPhone: '+91 98220 78901', secondaryPhone: '+91 98220 78902', remainingMinutes: 75, dailyLimitMin: 15, validityStart: '2026-06-01', validityExpiry: '2026-11-22', validityStatus: 'Expiring', assignedDevice: 'DEV-7702 (Sarojini Sadan Booth 1)', status: 'Active', addedDate: '2026-06-01' },
      { id: 'STU-4007', studentCode: 'S2D-DOON-8807', name: 'Rohan Gupta', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 11', section: 'Section A', hostelWing: 'Tagore Bhavan · Rm 102', guardianName: 'Manoj Gupta', guardianRelation: 'Father', primaryPhone: '+91 98105 89012', secondaryPhone: '+91 98105 89013', remainingMinutes: 190, dailyLimitMin: 15, validityStart: '2026-08-15', validityExpiry: '2027-05-30', validityStatus: 'Active', assignedDevice: 'DEV-7701 (Tagore Bhavan Booth 1)', status: 'Active', addedDate: '2026-08-15' },
      { id: 'STU-4008', studentCode: 'S2D-DOON-8808', name: 'Kavya Reddy', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 9', section: 'Section C', hostelWing: 'Sarojini Sadan · Rm 118', guardianName: 'Suresh Reddy', guardianRelation: 'Father', primaryPhone: '+91 98490 90123', secondaryPhone: '+91 98490 90124', remainingMinutes: 110, dailyLimitMin: 15, validityStart: '2026-08-15', validityExpiry: '2027-05-30', validityStatus: 'Active', assignedDevice: 'DEV-7703 (Sarojini Sadan Booth 2)', status: 'Active', addedDate: '2026-08-16' },
      { id: 'STU-4009', studentCode: 'S2D-DOON-8809', name: 'Ishaan Sharma', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 12', section: 'Section A', hostelWing: 'Tagore Bhavan · Rm 401', guardianName: 'Pooja Sharma', guardianRelation: 'Mother', primaryPhone: '+91 98112 01234', secondaryPhone: '+91 98112 01235', remainingMinutes: 30, dailyLimitMin: 15, validityStart: '2026-05-20', validityExpiry: '2026-11-20', validityStatus: 'Expiring', assignedDevice: 'DEV-7701 (Tagore Bhavan Booth 1)', status: 'Active', addedDate: '2026-05-20' },
      { id: 'STU-4010', studentCode: 'S2D-DOON-8810', name: 'Priya Nair', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 10', section: 'Section A', hostelWing: 'Sarojini Sadan · Rm 220', guardianName: 'Radha Nair', guardianRelation: 'Mother', primaryPhone: '+91 98471 12345', secondaryPhone: '+91 98471 12346', remainingMinutes: 240, dailyLimitMin: 20, validityStart: '2026-09-01', validityExpiry: '2027-06-30', validityStatus: 'Active', assignedDevice: 'DEV-7702 (Sarojini Sadan Booth 1)', status: 'Active', addedDate: '2026-09-01' },
      { id: 'STU-4011', studentCode: 'S2D-DOON-8811', name: 'Aryan Joshi', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 7', section: 'Section B', hostelWing: 'Junior Wing · Rm 112', guardianName: 'Deepak Joshi', guardianRelation: 'Father', primaryPhone: '+91 98260 23456', secondaryPhone: '+91 98260 23457', remainingMinutes: 130, dailyLimitMin: 10, validityStart: '2026-08-20', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7704 (Junior Wing Kiosk)', status: 'Active', addedDate: '2026-08-20' },
      { id: 'STU-4012', studentCode: 'S2D-DOON-8812', name: 'Saanvi Kulkarni', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 11', section: 'Section B', hostelWing: 'Sarojini Sadan · Rm 310', guardianName: 'Mahesh Kulkarni', guardianRelation: 'Father', primaryPhone: '+91 98230 34567', secondaryPhone: '+91 98230 34568', remainingMinutes: 160, dailyLimitMin: 15, validityStart: '2026-08-01', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7703 (Sarojini Sadan Booth 2)', status: 'Active', addedDate: '2026-08-05' },
      { id: 'STU-4013', studentCode: 'S2D-DOON-8813', name: 'Kabir Malhotra', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 8', section: 'Section C', hostelWing: 'Junior Wing · Rm 115', guardianName: 'Amit Malhotra', guardianRelation: 'Father', primaryPhone: '+91 98103 45678', secondaryPhone: '+91 98103 45679', remainingMinutes: 85, dailyLimitMin: 10, validityStart: '2026-08-01', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7704 (Junior Wing Kiosk)', status: 'Active', addedDate: '2026-08-01' },
      { id: 'STU-4014', studentCode: 'S2D-DOON-8814', name: 'Anika Choudhury', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 10', section: 'Section C', hostelWing: 'Sarojini Sadan · Rm 222', guardianName: 'Bikram Choudhury', guardianRelation: 'Father', primaryPhone: '+91 98310 56789', secondaryPhone: '+91 98310 56790', remainingMinutes: 200, dailyLimitMin: 15, validityStart: '2026-08-01', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7702 (Sarojini Sadan Booth 1)', status: 'Active', addedDate: '2026-08-01' },
      { id: 'STU-4015', studentCode: 'S2D-DOON-8815', name: 'Dhruv Singhal', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchiseId: 'FRN-101', className: 'Grade 12', section: 'Section B', hostelWing: 'Tagore Bhavan · Rm 405', guardianName: 'Alok Singhal', guardianRelation: 'Father', primaryPhone: '+91 98107 67890', secondaryPhone: '+91 98107 67891', remainingMinutes: 140, dailyLimitMin: 20, validityStart: '2026-08-01', validityExpiry: '2027-05-31', validityStatus: 'Active', assignedDevice: 'DEV-7701 (Tagore Bhavan Booth 1)', status: 'Active', addedDate: '2026-08-01' }
    ],

    classes: [
      { id: 'CLS-07', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', className: 'Grade 7', supervisor: 'Smt. Nalini Sharma', sectionsCount: 3, studentsCount: 92, activeAccounts: 89, defaultDailyMinutes: 10, scheduleGroup: 'Junior Evening Window', status: 'Active' },
      { id: 'CLS-08', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', className: 'Grade 8', supervisor: 'Shri Lokesh Gupta', sectionsCount: 3, studentsCount: 104, activeAccounts: 98, defaultDailyMinutes: 10, scheduleGroup: 'Junior Evening Window', status: 'Active' },
      { id: 'CLS-09', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', className: 'Grade 9', supervisor: 'Dr. Sunita Rao', sectionsCount: 4, studentsCount: 122, activeAccounts: 119, defaultDailyMinutes: 15, scheduleGroup: 'Standard Hostel Window', status: 'Active' },
      { id: 'CLS-10', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', className: 'Grade 10', supervisor: 'Prof. Manmohan Verma', sectionsCount: 4, studentsCount: 128, activeAccounts: 125, defaultDailyMinutes: 15, scheduleGroup: 'Standard Hostel Window', status: 'Active' },
      { id: 'CLS-11', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', className: 'Grade 11', supervisor: 'Dr. Arvind Trivedi', sectionsCount: 3, studentsCount: 118, activeAccounts: 111, defaultDailyMinutes: 15, scheduleGroup: 'Senior Study-Safe Window', status: 'Active' },
      { id: 'CLS-12', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', className: 'Grade 12', supervisor: 'Prof. Harishankar Pandey', sectionsCount: 3, studentsCount: 120, activeAccounts: 116, defaultDailyMinutes: 20, scheduleGroup: 'Senior Study-Safe Window', status: 'Active' }
    ],

    sections: [
      { id: 'SEC-10A', classId: 'CLS-10', className: 'Grade 10', sectionName: 'Section A', roomWing: 'Tagore Bhavan · Floor 2', advisor: 'Prof. Manmohan Verma', studentsCount: 34, activeCallers: 34, assignedBooth: 'Tagore Bhavan Booth 1', status: 'Active' },
      { id: 'SEC-10B', classId: 'CLS-10', className: 'Grade 10', sectionName: 'Section B', roomWing: 'Sarojini Sadan · Floor 2', advisor: 'Smt. Kavita Pillai', studentsCount: 32, activeCallers: 31, assignedBooth: 'Sarojini Sadan Booth 1', status: 'Active' },
      { id: 'SEC-09B', classId: 'CLS-09', className: 'Grade 9', sectionName: 'Section B', roomWing: 'Sarojini Sadan · Floor 1', advisor: 'Dr. Sunita Rao', studentsCount: 31, activeCallers: 30, assignedBooth: 'Sarojini Sadan Booth 1', status: 'Active' },
      { id: 'SEC-11A', classId: 'CLS-11', className: 'Grade 11', sectionName: 'Section A', roomWing: 'Tagore Bhavan · Floor 3', advisor: 'Dr. Arvind Trivedi', studentsCount: 39, activeCallers: 37, assignedBooth: 'Tagore Bhavan Booth 2', status: 'Active' },
      { id: 'SEC-12C', classId: 'CLS-12', className: 'Grade 12', sectionName: 'Section C', roomWing: 'Sarojini Sadan · Floor 3', advisor: 'Prof. Harishankar Pandey', studentsCount: 40, activeCallers: 39, assignedBooth: 'Sarojini Sadan Booth 2', status: 'Active' },
      { id: 'SEC-08A', classId: 'CLS-08', className: 'Grade 8', sectionName: 'Section A', roomWing: 'Junior Wing · Floor 1', advisor: 'Shri Lokesh Gupta', studentsCount: 35, activeCallers: 32, assignedBooth: 'Junior Wing Kiosk', status: 'Active' }
    ],

    guardians: [
      { id: 'GRD-501', name: 'Rajesh Sharma', studentId: 'STU-4001', studentName: 'Aarav Sharma', className: 'Grade 10 · Sec A', relation: 'Father', fatherPhone: '+91 98101 23456', motherPhone: '+91 98101 23457', emergencyPhone: '+91 98101 23499', email: 'rajesh.sharma@example.in', verification: 'KYC Verified (Aadhaar)', whitelistStatus: 'Authorized (2 Numbers)', status: 'Active' },
      { id: 'GRD-502', name: 'Meenakshi Iyer', studentId: 'STU-4002', studentName: 'Ananya Iyer', className: 'Grade 9 · Sec B', relation: 'Mother', fatherPhone: '+91 98450 34568', motherPhone: '+91 98450 34567', emergencyPhone: '+91 98450 34500', email: 'meenakshi.iyer@example.in', verification: 'KYC Verified (Aadhaar)', whitelistStatus: 'Authorized (2 Numbers)', status: 'Active' },
      { id: 'GRD-503', name: 'Sunil Patel', studentId: 'STU-4003', studentName: 'Vihaan Patel', className: 'Grade 11 · Sec A', relation: 'Father', fatherPhone: '+91 98250 45678', motherPhone: '+91 98250 45679', emergencyPhone: 'None', email: 'sunil.patel@example.in', verification: 'KYC Verified (Aadhaar)', whitelistStatus: 'Authorized (2 Numbers)', status: 'Active' },
      { id: 'GRD-504', name: 'Sunita Sen', studentId: 'STU-4004', studentName: 'Diya Sen', className: 'Grade 12 · Sec C', relation: 'Mother', fatherPhone: '+91 98300 56790', motherPhone: '+91 98300 56789', emergencyPhone: '+91 98300 56700', email: 'sunita.sen@example.in', verification: 'KYC Verified (Aadhaar)', whitelistStatus: 'Authorized (2 Numbers)', status: 'Active' },
      { id: 'GRD-505', name: 'Vikram Verma', studentId: 'STU-4005', studentName: 'Aditya Verma', className: 'Grade 8 · Sec A', relation: 'Father', fatherPhone: '+91 98110 67890', motherPhone: '+91 98110 67891', emergencyPhone: 'None', email: 'vikram.verma@example.in', verification: 'Pending Renewal', whitelistStatus: 'Paused (Account Expired)', status: 'Inactive' },
      { id: 'GRD-506', name: 'Ashok Deshmukh', studentId: 'STU-4006', studentName: 'Tanvi Deshmukh', className: 'Grade 10 · Sec B', relation: 'Father', fatherPhone: '+91 98220 78901', motherPhone: '+91 98220 78902', emergencyPhone: '+91 98220 78900', email: 'ashok.deshmukh@example.in', verification: 'KYC Verified (Aadhaar)', whitelistStatus: 'Authorized (2 Numbers)', status: 'Active' }
    ],

    studentCodes: [
      { id: 'COD-701', code: 'S2D-DOON-8801', studentId: 'STU-4001', studentName: 'Aarav Sharma', className: 'Grade 10 · Sec A', issuedBy: 'Backend Auth Engine', issuedAt: '2026-08-01 10:14', lastUsed: '2026-11-09 19:22', pinPolicy: 'Code + Student PIN', status: 'Active' },
      { id: 'COD-702', code: 'S2D-DOON-8802', studentId: 'STU-4002', studentName: 'Ananya Iyer', className: 'Grade 9 · Sec B', issuedBy: 'Backend Auth Engine', issuedAt: '2026-08-02 11:05', lastUsed: '2026-11-10 07:40', pinPolicy: 'Code + 4-Digit Student PIN', status: 'Active' },
      { id: 'COD-703', code: 'S2D-DOON-8803', studentId: 'STU-4003', studentName: 'Vihaan Patel', className: 'Grade 11 · Sec A', issuedBy: 'Backend Auth Engine', issuedAt: '2026-05-15 09:30', lastUsed: '2026-11-08 20:10', pinPolicy: 'Code + 4-Digit Student PIN', status: 'Active' },
      { id: 'COD-704', code: 'S2D-DOON-8804', studentId: 'STU-4004', studentName: 'Diya Sen', className: 'Grade 12 · Sec C', issuedBy: 'Backend Auth Engine', issuedAt: '2026-08-10 14:18', lastUsed: '2026-11-09 20:45', pinPolicy: 'Code + 4-Digit Student PIN', status: 'Active' },
      { id: 'COD-705', code: 'S2D-DOON-8805', studentId: 'STU-4005', studentName: 'Aditya Verma', className: 'Grade 8 · Sec A', issuedBy: 'Backend Auth Engine', issuedAt: '2026-04-01 08:50', lastUsed: '2026-10-29 18:15', pinPolicy: 'Suspended (Validity Expired)', status: 'Suspended' },
      { id: 'COD-706', code: 'S2D-DOON-8806', studentId: 'STU-4006', studentName: 'Tanvi Deshmukh', className: 'Grade 10 · Sec B', issuedBy: 'Backend Auth Engine', issuedAt: '2026-06-01 09:15', lastUsed: '2026-11-09 18:30', pinPolicy: 'Code + 4-Digit Student PIN', status: 'Active' }
    ],

    rechargePlans: [
      { id: 'RPL-01', name: 'Starter Monthly Pack', price: 199.00, minutes: 100, validityDays: 30, perCallCap: '10 mins', applicability: 'All Schools', popular: false, status: 'Active' },
      { id: 'RPL-02', name: 'Standard Term Calling Pack', price: 499.00, minutes: 300, validityDays: 90, perCallCap: '15 mins', applicability: 'All Schools', popular: true, status: 'Active' },
      { id: 'RPL-03', name: 'Full Academic Year Pack', price: 1499.00, minutes: 1000, validityDays: 365, perCallCap: '15 mins', applicability: 'Boarding Schools', popular: true, status: 'Active' },
      { id: 'RPL-04', name: 'Senior Scholar Extended Pack', price: 1999.00, minutes: 1500, validityDays: 365, perCallCap: '20 mins', applicability: 'Grades 11–12', popular: false, status: 'Active' },
      { id: 'RPL-05', name: 'Emergency Top-Up Booster', price: 99.00, minutes: 45, validityDays: 14, perCallCap: '10 mins', applicability: 'Warden / Admin Approved', popular: false, status: 'Active' }
    ],

    recharges: [
      { id: 'RCH-8001', date: '2026-11-10 08:30', studentId: 'STU-4001', studentName: 'Aarav Sharma', studentCode: 'S2D-DOON-8801', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', planName: 'Standard Term Calling Pack', amount: 499.00, minutesAdded: 300, validityDays: 90, paymentMode: 'UPI / Razorpay', status: 'Successful' },
      { id: 'RCH-8002', date: '2026-11-10 07:45', studentId: 'STU-4002', studentName: 'Ananya Iyer', studentCode: 'S2D-DOON-8802', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', planName: 'Starter Monthly Pack', amount: 199.00, minutesAdded: 100, validityDays: 30, paymentMode: 'Net Banking', status: 'Successful' },
      { id: 'RCH-8003', date: '2026-11-09 18:12', studentId: 'STU-4007', studentName: 'Rohan Gupta', studentCode: 'S2D-DOON-8807', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', planName: 'Full Academic Year Pack', amount: 1499.00, minutesAdded: 1000, validityDays: 365, paymentMode: 'UPI / PhonePe', status: 'Successful' },
      { id: 'RCH-8004', date: '2026-11-09 15:40', studentId: 'STU-4003', studentName: 'Vihaan Patel', studentCode: 'S2D-DOON-8803', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', planName: 'Standard Term Calling Pack', amount: 499.00, minutesAdded: 300, validityDays: 90, paymentMode: 'School Desk Cash', status: 'Pending' },
      { id: 'RCH-8005', date: '2026-11-09 12:05', studentId: 'STU-4010', studentName: 'Priya Nair', studentCode: 'S2D-DOON-8810', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', planName: 'Full Academic Year Pack', amount: 1499.00, minutesAdded: 1000, validityDays: 365, paymentMode: 'UPI / GooglePay', status: 'Successful' },
      { id: 'RCH-8006', date: '2026-11-08 17:20', studentId: 'STU-4005', studentName: 'Aditya Verma', studentCode: 'S2D-DOON-8805', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', planName: 'Emergency Top-Up Booster', amount: 99.00, minutesAdded: 45, validityDays: 14, paymentMode: 'Debit Card', status: 'Failed' }
    ],

    subscriptions: [
      { id: 'SUB-9001', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', planName: 'Enterprise Boarding Annual', billingCycle: 'Annual', studentSeats: 750, deviceSeats: 35, amount: 150000.00, startDate: '2026-08-15', expiryDate: '2027-08-15', autoRenew: 'Enabled', status: 'Active' },
      { id: 'SUB-9002', schoolId: 'SCH-1002', school: 'Mayo International Boarding School', franchise: 'Central Heartland Edutech', planName: 'Campus Growth Annual', billingCycle: 'Annual', studentSeats: 550, deviceSeats: 25, amount: 95000.00, startDate: '2026-05-30', expiryDate: '2027-05-30', autoRenew: 'Enabled', status: 'Active' },
      { id: 'SUB-9003', schoolId: 'SCH-1003', school: 'Scindia Residential Campus', franchise: 'Central Heartland Edutech', planName: 'Campus Growth Annual', billingCycle: 'Annual', studentSeats: 450, deviceSeats: 20, amount: 95000.00, startDate: '2025-11-24', expiryDate: '2026-11-24', autoRenew: 'Manual Invoice', status: 'Expiring' },
      { id: 'SUB-9004', schoolId: 'SCH-1004', school: 'Bishop Cotton Boys School & Hostel', franchise: 'North India EduNet Partners', planName: 'Enterprise Boarding Annual', billingCycle: 'Annual', studentSeats: 850, deviceSeats: 40, amount: 150000.00, startDate: '2026-09-01', expiryDate: '2027-09-01', autoRenew: 'Enabled', status: 'Active' },
      { id: 'SUB-9005', schoolId: 'SCH-1005', school: 'Sahyadri International Residential School', franchise: 'Western Scholastic Network', planName: 'Standard Hostel Quarterly', billingCycle: 'Quarterly', studentSeats: 350, deviceSeats: 15, amount: 35000.00, startDate: '2026-01-15', expiryDate: '2027-01-15', autoRenew: 'Enabled', status: 'Active' }
    ],

    transactions: [
      { id: 'TXN-30001', date: '2026-11-10 08:30', entity: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', category: 'Student Recharge', reference: 'PAY-RZP-994821A', method: 'UPI / PhonePe', amount: 499.00, status: 'Successful' },
      { id: 'TXN-30002', date: '2026-11-09 19:05', entity: 'Bishop Cotton Boys School', franchise: 'North India EduNet Partners', category: 'Annual Subscription', reference: 'NEFT-2026-8840', method: 'Institutional NEFT', amount: 150000.00, status: 'Successful' },
      { id: 'TXN-30003', date: '2026-11-09 15:40', entity: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', category: 'Bulk Credit Allocation', reference: 'IMPS-773019B', method: 'IMPS Bank Transfer', amount: 25000.00, status: 'Pending' },
      { id: 'TXN-30004', date: '2026-11-09 11:20', entity: 'Scindia Residential Campus', franchise: 'Central Heartland Edutech', category: 'Subscription Renewal', reference: 'CHQ-2026-8832', method: 'Institutional Cheque', amount: 95000.00, status: 'Pending' },
      { id: 'TXN-30005', date: '2026-11-08 17:20', entity: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', category: 'Student Recharge', reference: 'PAY-RZP-994702F', method: 'RuPay Debit Card', amount: 99.00, status: 'Failed' },
      { id: 'TXN-30006', date: '2026-11-07 14:15', entity: 'Mayo International Boarding', franchise: 'Central Heartland Edutech', category: 'Duplicate Top-Up Reversal', reference: 'RFD-2026-0412', method: 'UPI Reversal', amount: 499.00, status: 'Refunded' }
    ],

    commissions: [
      { id: 'COM-5001', period: 'Nov 2026 (MTD)', school: 'Doon Valley Residential Academy', sourceType: 'Recharges & Credits', grossAmount: 48200.00, rate: '18%', commissionEarned: 8676.00, payoutDate: '2026-12-05', status: 'Pending' },
      { id: 'COM-5002', period: 'Nov 2026 (MTD)', school: 'Bishop Cotton Boys School', sourceType: 'Recharges & Credits', grossAmount: 31900.00, rate: '18%', commissionEarned: 5742.00, payoutDate: '2026-12-05', status: 'Pending' },
      { id: 'COM-5003', period: 'Oct 2026', school: 'Doon Valley Residential Academy', sourceType: 'Subscription + Recharges', grossAmount: 142000.00, rate: '18%', commissionEarned: 25560.00, payoutDate: '2026-11-05', status: 'Successful' },
      { id: 'COM-5004', period: 'Oct 2026', school: 'Bishop Cotton Boys School', sourceType: 'Recharges & Credits', grossAmount: 64500.00, rate: '18%', commissionEarned: 11610.00, payoutDate: '2026-11-05', status: 'Successful' },
      { id: 'COM-5005', period: 'Oct 2026', school: 'Mayo International Boarding School', sourceType: 'Recharges & Credits', grossAmount: 41200.00, rate: '18%', commissionEarned: 7416.00, payoutDate: '2026-11-05', status: 'Successful' },
      { id: 'COM-5006', period: 'Sep 2026', school: 'Doon Valley Residential Academy', sourceType: 'Annual Onboarding Bonus + Credits', grossAmount: 198000.00, rate: '18%', commissionEarned: 35640.00, payoutDate: '2026-10-05', status: 'Successful' }
    ],

    devices: [
      { id: 'DEV-7701', deviceName: 'Tagore Bhavan Booth 1', serialNumber: 'S2D-TAB-90811A', imei: '358920104481901', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', wingLocation: 'Tagore Bhavan · Floor 2', assignedMode: 'Shared Hostel Booth (34 Students)', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '2 mins ago', status: 'Active' },
      { id: 'DEV-7702', deviceName: 'Sarojini Sadan Booth 1', serialNumber: 'S2D-TAB-90812B', imei: '358920104481902', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', wingLocation: 'Sarojini Sadan · Floor 1', assignedMode: 'Shared Hostel Booth (61 Students)', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '1 min ago', status: 'Active' },
      { id: 'DEV-7703', deviceName: 'Sarojini Sadan Booth 2', serialNumber: 'S2D-TAB-90813C', imei: '358920104481903', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', wingLocation: 'Sarojini Sadan · Floor 3', assignedMode: 'Shared Hostel Booth (40 Students)', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '4 mins ago', status: 'Active' },
      { id: 'DEV-7704', deviceName: 'Junior Wing Kiosk', serialNumber: 'S2D-TAB-90814D', imei: '358920104481904', model: 'Lenovo Tab K11 Kiosk Edition', schoolId: 'SCH-1001', school: 'Doon Valley Residential Academy', wingLocation: 'Junior Wing · Warden Desk', assignedMode: 'Warden-Supervised Kiosk', appVersion: 'v4.8.1-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Offline', lastHeartbeat: '3 hours ago', status: 'Active' },
      { id: 'DEV-7705', deviceName: 'Mayo Main Hostel Booth', serialNumber: 'S2D-TAB-90821E', imei: '358920104482105', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1002', school: 'Mayo International Boarding School', wingLocation: 'Main Block · Lobby', assignedMode: 'Shared Hostel Booth', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: 'Just now', status: 'Active' },
      { id: 'DEV-7706', deviceName: 'Bishop Cotton Senior Kiosk', serialNumber: 'S2D-TAB-90841H', imei: '358920104484108', model: 'Samsung Galaxy Tab Active5 Enterprise', schoolId: 'SCH-1004', school: 'Bishop Cotton Boys School & Hostel', wingLocation: 'Senior Dorm · Commons', assignedMode: 'Shared Hostel Booth', appVersion: 'v4.8.2-kiosk', enrollmentStatus: 'Enrolled (AE Dedicated)', kioskCompliance: 'Compliant', onlineStatus: 'Online', lastHeartbeat: '1 min ago', status: 'Active' }
    ],

    callHistory: [
      { id: 'CAL-99001', startTime: '2026-11-10 07:40', dateOnly: '2026-11-10', studentName: 'Ananya Iyer', studentCode: 'S2D-DOON-8802', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', guardianName: 'Meenakshi Iyer (Mother)', authorizedNumber: '+91 98450 34567', device: 'DEV-7702', duration: '08m 42s', minutesUsed: 9, remainingAfter: 120, disconnectReason: 'Normal Student Hangup', status: 'Completed' },
      { id: 'CAL-99002', startTime: '2026-11-09 20:45', dateOnly: '2026-11-09', studentName: 'Diya Sen', studentCode: 'S2D-DOON-8804', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', guardianName: 'Sunita Sen (Mother)', authorizedNumber: '+91 98300 56789', device: 'DEV-7703', duration: '14m 58s', minutesUsed: 15, remainingAfter: 215, disconnectReason: 'Max Per-Call Cap Reached', status: 'Completed' },
      { id: 'CAL-99003', startTime: '2026-11-09 19:22', dateOnly: '2026-11-09', studentName: 'Aarav Sharma', studentCode: 'S2D-DOON-8801', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', guardianName: 'Rajesh Sharma (Father)', authorizedNumber: '+91 98101 23456', device: 'DEV-7701', duration: '11m 15s', minutesUsed: 12, remainingAfter: 180, disconnectReason: 'Normal Guardian Hangup', status: 'Completed' },
      { id: 'CAL-99004', startTime: '2026-11-09 19:05', dateOnly: '2026-11-09', studentName: 'Tanvi Deshmukh', studentCode: 'S2D-DOON-8806', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', guardianName: 'Ashok Deshmukh (Father)', authorizedNumber: '+91 98220 78901', device: 'DEV-7702', duration: '00m 00s', minutesUsed: 0, remainingAfter: 75, disconnectReason: 'No Answer at Destination', status: 'Missed' },
      { id: 'CAL-99005', startTime: '2026-11-09 18:50', dateOnly: '2026-11-09', studentName: 'Rohan Gupta', studentCode: 'S2D-DOON-8807', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', guardianName: 'Manoj Gupta (Father)', authorizedNumber: '+91 98105 89012', device: 'DEV-7701', duration: '09m 30s', minutesUsed: 10, remainingAfter: 190, disconnectReason: 'Normal Hangup', status: 'Completed' },
      { id: 'CAL-99006', startTime: '2026-11-09 14:12', dateOnly: '2026-11-09', studentName: 'Vihaan Patel', studentCode: 'S2D-DOON-8803', school: 'Doon Valley Residential Academy', franchise: 'North India EduNet Partners', guardianName: 'Sunil Patel (Father)', authorizedNumber: '+91 98250 45678', device: 'DEV-7701', duration: '00m 00s', minutesUsed: 0, remainingAfter: 24, disconnectReason: 'Blocked: Academic Class Hours', status: 'Restricted' }
    ],

    wardens: [
      { id: 'WRD-601', name: 'Major Rajeshwar Singh (Retd.)', email: 'r.singh@doonvalley.edu.in', phone: '+91 98101 23481', hostelWing: 'Tagore Bhavan (Boys Grades 10–12)', shiftHours: '16:00 – 00:00', supervisedStudents: 185, supervisedDevices: 8, emergencyOverride: 'Authorized', status: 'Active' },
      { id: 'WRD-602', name: 'Smt. Shanti Devi', email: 's.devi@doonvalley.edu.in', phone: '+91 98101 23482', hostelWing: 'Sarojini Sadan (Girls Grades 9–12)', shiftHours: '15:00 – 23:00', supervisedStudents: 240, supervisedDevices: 10, emergencyOverride: 'Authorized', status: 'Active' },
      { id: 'WRD-603', name: 'Shri Simon Murmu', email: 's.murmu@doonvalley.edu.in', phone: '+91 98101 23483', hostelWing: 'Junior Wing (Grades 7–8)', shiftHours: '15:30 – 22:00', supervisedStudents: 196, supervisedDevices: 6, emergencyOverride: 'Authorized', status: 'Active' },
      { id: 'WRD-604', name: 'Smt. Geeta Goswami', email: 'g.goswami@doonvalley.edu.in', phone: '+91 98101 23484', hostelWing: 'All Wings · Night Relief', shiftHours: '23:00 – 07:00', supervisedStudents: 684, supervisedDevices: 28, emergencyOverride: 'Emergency Only', status: 'Active' }
    ],

    roles: [
      { id: 'ROL-01', name: 'Super Administrator', scope: 'Global Platform', usersCount: 3, description: 'Full governance across franchises, schools, billing, Android Enterprise policy, and IAM.', systemLocked: true, status: 'Active' },
      { id: 'ROL-02', name: 'Platform Finance Controller', scope: 'National Finance', usersCount: 4, description: 'Manages subscriptions, gateway settlements, refunds, recharge plans, and franchise payouts in INR.', systemLocked: false, status: 'Active' },
      { id: 'ROL-03', name: 'Franchise Partner Director', scope: 'Assigned Territory', usersCount: 14, description: 'Manages assigned schools, bulk student onboarding, credit allocations, and commission ledgers.', systemLocked: true, status: 'Active' },
      { id: 'ROL-04', name: 'School Principal / Primary Admin', scope: 'Single Campus', usersCount: 52, description: 'Full campus control over students, guardians, schedules, wardens, recharges, and booth devices.', systemLocked: true, status: 'Active' },
      { id: 'ROL-05', name: 'Hostel Chief Warden', scope: 'Hostel Wing', usersCount: 118, description: 'Supervises calling schedules, device booths, emergency call overrides, and call logs.', systemLocked: false, status: 'Active' },
      { id: 'ROL-06', name: 'Compliance & Audit Viewer', scope: 'Read-Only Global', usersCount: 2, description: 'Read-only inspection of call logs, guardian authorization trails, and security audit logs.', systemLocked: false, status: 'Active' }
    ],

    auditLogs: [
      { id: 'AUD-901', timestamp: '2026-11-10 08:44:12', actor: 'Aarav Singhal (Super Admin)', module: 'Calling Duration', action: 'Updated Global Max Per-Call Cap', target: 'Global Policy (20m ceiling)', ipAddress: '103.21.244.14', severity: 'Info' },
      { id: 'AUD-902', timestamp: '2026-11-10 08:15:04', actor: 'Dr. Ramesh Chandra Sharma (School Admin)', module: 'Guardian Whitelist', action: 'Verified Secondary Guardian Number', target: 'STU-4002 · Ananya Iyer', ipAddress: '103.45.12.88', severity: 'Info' },
      { id: 'AUD-903', timestamp: '2026-11-09 21:10:39', actor: 'System Policy Engine', module: 'Device Compliance', action: 'Flagged Kiosk Policy Drift', target: 'DEV-7704 · Junior Wing Kiosk', ipAddress: 'Internal Worker', severity: 'Warning' },
      { id: 'AUD-904', timestamp: '2026-11-09 16:02:51', actor: 'Vikramaditya Singhania (Franchise)', module: 'Recharge Allocation', action: 'Submitted Bulk Credit Request', target: 'Doon Valley Residential Academy (₹25,000)', ipAddress: '103.88.45.22', severity: 'Info' }
    ],

    notifications: [
      { id: 'NTF-01', title: 'Subscription Renewal Due in 14 Days', desc: 'Scindia Residential Campus (SCH-1003) expires on Nov 24, 2026.', time: '18 mins ago', category: 'Billing', unread: true },
      { id: 'NTF-02', title: '3 Student Validities Expiring Soon', desc: 'Vihaan Patel, Ishaan Sharma, Tanvi Deshmukh accounts expiring within 14 days.', time: '1 hour ago', category: 'Validity', unread: true },
      { id: 'NTF-03', title: 'Device Heartbeat Delayed', desc: 'DEV-7704 (Junior Wing Kiosk) has been offline for 3 hours.', time: '3 hours ago', category: 'Device', unread: false },
      { id: 'NTF-04', title: 'Monthly Commission Batch Ready', desc: 'November MTD ledger reconciled for active franchises.', time: 'Yesterday', category: 'Finance', unread: false }
    ]
  };

  window.S2D_DEMO = S2D_DEMO;
})(window);
