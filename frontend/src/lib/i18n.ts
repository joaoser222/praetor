/**
 * Mensagens globais para toda a aplicação.
 * Strings genéricas que se aplicam a todas as features (ações de CRUD, elementos comuns de UI, etc.)
 */
export const zodMessages = {
    required: (field: string) => `${field} é obrigatório`,
    invalidEmail: 'Endereço de e-mail inválido',
    tooShort: (field: string, min: number) => `${field} deve ter pelo menos ${min} caracteres`,
    tooLong: (field: string, max: number) => `${field} deve ter no máximo ${max} caracteres`,
};

export const commonMessages = {
    loading: 'Carregando...',
    actions: 'Ações',
    delete: 'Excluir',
    edit: 'Editar',
    save: 'Salvar',
    cancel: 'Cancelar',
    confirmDelete: 'Tem certeza de que deseja excluir este item?',
    noItems: 'Nenhum item encontrado.',
    add: 'Adicionar novo',
    saveFailed: 'Não foi possível salvar. Tente novamente.',
    deleteFailed: 'Não foi possível excluir. Tente novamente.',
    loadFailed: 'Não foi possível carregar os dados.',
};
