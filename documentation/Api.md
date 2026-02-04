## API's for communication

### (1) Authorization apis
> 1. **Task:** Authorize the users based on credentials received  
**Authority:** `Anyone`  
**Method:** POST  
**API:** v1/auth/login  

### (2) Admin apis
> 1. **Task:** Configure organization details  
**Authority:** `Admin`  
**Method:** POST  
**API:** v1/admin/config-org

> 2. **Task:** Configure system and camera details  
**Authority:** `Admin`  
**Method:** POST  
**API:** v1/admin/system-config  

> 3. **Task:** System health checkup  
**Authority:** `Admin`  
**Method:** GET  
**API:** v1/admin/system-health  

> 4. **Task:** Add Operator  
**Authority:** `Admin`  
**Method:** POST  
**API:** v1/admin/add-operator

> 5. **Task:** Update operator details  
**Authority:** `Admin`  
**Method:** PATCH  
**API:** v1/admin/update-operator/{id}

> 6. **Task:** View operator details  
**Authority:** `Admin`  
**Method:** GET  
**API:** v1/admin/view-operator/{id}

> 7. **Task:** Delete operator  
**Authority:** `Admin`  
**Method:** DELETE  
**API:** v1/admin/delete-operator/{id} 

> 8. **Task:** Get operators list  
**Authority:** `Admin`    
**Method:** GET  
**API:** v1/admin/get-operators

### (3) Operators apis
> 1. **Task:** Add user  
**Authority:** `Admin` `Operator`  
**Method:** POST  
**API:** v1/ops/add-user

> 2. **Task:** Get users list  
**Authority:** `Admin` `Operator`   
**Method:** GET  
**API:** v1/ops/get-users

> 3. **Task:** Get operators list  
**Authority:** `Admin`  `Operator`  
**Method:** PATCH  
**API:** v1/ops/update-user/{id}

> 4. **Task:** Get operators list  
**Authority:** `Admin`  `Operator`  
**Method:** DELETE  
**API:** v1/ops/delete-user/{id}

> 5. **Task:** Get User  
**Authority:** `Admin`  `Operator`  
**Method:** GET  
**API:** v1/ops/get-user/{id}

> 6. **Task:** Upload image for attendance processing
**Authority:** `Admin`  `Operator`  
**Method:** POST  
**API:** v1/ops/upload-image

> 7. **Task:** Mark manual attendance   
**Authority:** `Admin`  `Operator`  
**Method:** POST  
**API:** v1/ops/mark-attendance

> 8. **Task:** Get audit logs  
**Authority:** `Admin`  `Operator`  
**Method:** GET  
**API:** v1/ops/get-logs

### (4) User apis
> 1. **Task:** View personal attendance  
**Authority:** `User`  
**Method:** GET  
**API:** v1/user/get-attendance