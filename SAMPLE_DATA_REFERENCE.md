# Sample Data Reference Guide

## Available Clients for Demo/Testing

Based on the actual sample data in `sample-data-set/clients.csv`, here are the **real client names** that can be used in queries and demonstrations:

### 🏢 **Top 20 Clients Available:**

1. **Saini LLC** (ID: 1) - New Delhi, Delhi
2. **Mann Group** (ID: 2) - New Delhi, Delhi  
3. **Zacharia, Sarkar and Dass** (ID: 3) - Chennai, Tamil Nadu
4. **Datta-Mand** (ID: 4) - Surat, Gujarat
5. **Kale PLC** (ID: 5) - Coimbatore, Tamil Nadu
6. **Zacharia-Mahal** (ID: 6) - Ahmedabad, Gujarat
7. **Wadhwa-Upadhyay** (ID: 7) - Nagpur, Maharashtra
8. **Tailor, Ganesh and Kuruvilla** (ID: 8) - Chennai, Tamil Nadu
9. **Deol Inc** (ID: 9) - Coimbatore, Tamil Nadu
10. **Yogi-Jaggi** (ID: 10) - Coimbatore, Tamil Nadu
11. **Savant-Chad** (ID: 11) - Mysuru, Karnataka
12. **Tella-Sheth** (ID: 12) - New Delhi, Delhi
13. **Vala-Raju** (ID: 13) - Surat, Gujarat
14. **Taneja and Sons** (ID: 14) - Ahmedabad, Gujarat
15. **Raman Ltd** (ID: 15) - Nagpur, Maharashtra
16. **Sankar and Sons** (ID: 16) - New Delhi, Delhi
17. **Lata-Khosla** (ID: 17) - New Delhi, Delhi
18. **Sura-Lall** (ID: 18) - Surat, Gujarat
19. **Chauhan, Swamy and Soman** (ID: 19) - New Delhi, Delhi
20. **Dasgupta Ltd** (ID: 20) - Chennai, Tamil Nadu

## 🎯 **Recommended Clients for Demos:**

### **For Simple Names:**
- **Mann Group** - Easy to pronounce, professional sounding
- **Kale PLC** - Short, corporate structure
- **Deol Inc** - Simple, modern sounding
- **Raman Ltd** - Classic business name

### **For Complex Names (Advanced Demos):**
- **Zacharia, Sarkar and Dass** - Partnership structure
- **Tailor, Ganesh and Kuruvilla** - Multi-partner firm
- **Chauhan, Swamy and Soman** - Professional services firm

## 🏙️ **Available Cities with Data:**

Based on order analysis, these cities have substantial data:

1. **New Delhi**: 2,002 orders
2. **Ahmedabad**: 1,023 orders  
3. **Coimbatore**: 1,021 orders
4. **Mysuru**: 1,021 orders
5. **Bengaluru**: 997 orders
6. **Surat**: 965 orders
7. **Chennai**: 964 orders
8. **Nagpur**: 684 orders
9. **Mumbai**: 673 orders
10. **Pune**: 650 orders

## 🏭 **Available Warehouses:**

Sample warehouses that can be used in queries:
- **Warehouse 1** - Surat, Gujarat
- **Warehouse 8** - Chennai, Tamil Nadu
- **Warehouse 6** - Bengaluru, Karnataka
- **Warehouse 5** - New Delhi, Delhi
- **Warehouse 3** - Ahmedabad, Gujarat

## 📅 **Data Date Range:**

- **Earliest Order**: January 1, 2025
- **Latest Order**: September 12, 2025
- **Best Months for Analysis**: July, August, September 2025

## ✅ **Working Query Examples:**

### **Client Analysis:**
```bash
python3 main.py --query "Why did Client Mann Group's orders fail in the past week?"
python3 main.py --query "Why did Client Kale PLC's orders fail in the past week?"
python3 main.py --query "Why did Client Deol Inc's orders fail in the past week?"
```

### **City Analysis:**
```bash
python3 main.py --query "Why were deliveries delayed in Chennai in August?"
python3 main.py --query "Why were deliveries delayed in Ahmedabad in July?"
python3 main.py --query "Why were deliveries delayed in Bengaluru in August?"
```

### **City Comparisons:**
```bash
python3 main.py --query "Compare delivery failure causes between Chennai and Coimbatore last month"
python3 main.py --query "Compare delivery failure causes between Ahmedabad and Surat last month"
python3 main.py --query "Compare delivery failure causes between Mumbai and Pune last month"
```

### **Warehouse Analysis:**
```bash
python3 main.py --query "Explain top reasons for delivery failures linked to Warehouse 1 in August"
python3 main.py --query "Explain top reasons for delivery failures linked to Warehouse 8 in July"
python3 main.py --query "Explain top reasons for delivery failures linked to Warehouse 6 in August"
```

## ❌ **Fictional Names to Avoid:**

These names do **NOT** exist in the sample data and will cause queries to fail:
- ❌ TechCorp
- ❌ Client ABC  
- ❌ RetailGiant
- ❌ Client 123 (unless referring to actual ID)
- ❌ Any "Corp" or "Corporation" names
- ❌ Western-style company names

## 🔧 **For Demo Script Updates:**

When updating demo scripts or documentation, always use:
1. **Real client names** from the list above
2. **Actual cities** with substantial data
3. **Existing warehouse names** from the sample data
4. **Valid date ranges** (Jan-Sep 2025)

This ensures all demonstrations work correctly with the actual sample data.

---

*Reference updated: 2025-09-29 - Based on actual sample data analysis*