# Project Roadmap Checklist

## 📌 Phase 1: Project Setup
- [x] Set up Django project and app
- [x] Configure database (PostgreSQL or other)
- [x] Create initial models for `Order`, `Part`, `OrderItem`, etc.
- [x] Implement user authentication and permissions
- [x] Set up Django admin for model management

## 📌 Phase 2: Database Schema & Models
- [x] Define `Order` model
  - [x] `name` field
  - [x] `customer` as ForeignKey to `User`
  - [x] `estimated_completion` DateField
  - [x] `status` as a `TextChoices`
- [x] Define `Part` model
  - [x] `name` field
  - [x] ForeignKeys for `PartType`, `Step`, `assigned_emp`, `customer`, `order`
  - [x] `estimated_completion` DateField
  - [x] Implement status as a `TextChoices`
- [x] Define `OrderItem` model linking `Order` and `Part`
- [x] Define `Part Type` model linking `Part` and `Step`
- [x] Define `Part Doc` model linking Documents to `Part`

## 📌 Phase 3: Views & Templates
- [ ] Customer Views
  - [x] `/tracker` list all orders and parts related to the customer
    - [ ] Sorting and Filtering
  - [x] `/login` using built in Django system for Auth and permissions
  - [x] `/password_reset`
  - [x] `/` Home page
- [ ] Employees Views
  - [ ] Consider moving over to `ModelForm` models for Parts and orders
    - The reason being that it seems Model Forms may make it easier to ensure validity for different fields which may be better than just going about it very much manually. Try and implement it for the documentation engine first, and then after make the decision to move `Parts` and `Orders` over to the `ModelForm` model format if it seems to be a better idea.
  - [x] `/edit` Shows all of the current `Parts` and `Orders` 
    - [ ] Sorting and Filtering
  - [x] `/edit_part/<part_id>`
  - [x] `/edit_order/<order_id>`
  - [ ] `/docs` list all documents for all orders and parts
    - [ ] Sorting
    - [ ] Filtering
  - [ ] `/doc/<docId>`
  - [ ] `/add_user`
  - [ ] `/dashboard` Fairly basic overview for the system
    - [ ] Current stats

## 📌 Phase 4: Frontend Enhancements
- [ ] Review CSS for all pages once basic features are done 
  - Potentially move over to using tailwind CSS for more granular control instead of the normal `styles.css` interface for doing styling.

## 📌 Phase 5: Deployment
- [ ] Email server for password reset

## 📌 Phase 6: Future Enhancements
- [ ] Implement notifications for status changes
- [ ] Add reporting and analytics features
- [ ] Optimize database queries and indexing
- 
---

This checklist provides a structured roadmap for developing your Django-based order tracking system. Let me know if you'd like additional details or refinements! 🚀

