/**
 * Global messages for the entire application.
 * Generic strings that apply to all features (CRUD actions, common UI elements, etc.)
 */
export const zodMessages = {
    required: (field: string) => `${field} is required`,
    invalidEmail: 'Invalid email address',
    tooShort: (field: string, min: number) => `${field} must be at least ${min} characters`,
    tooLong: (field: string, max: number) => `${field} must be at most ${max} characters`,
};

export const commonMessages = {
    loading: 'Loading...',
    actions: 'Actions',
    delete: 'Delete',
    edit: 'Edit',
    save: 'Save',
    cancel: 'Cancel',
    confirmDelete: 'Are you sure you want to delete this item?',
    noItems: 'No items found.',
    add: 'Add New',
};
