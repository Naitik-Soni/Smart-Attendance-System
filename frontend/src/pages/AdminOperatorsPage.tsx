import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

import { createOperator, deleteOperator, fetchOperators, updateOperator } from '../lib/api';
import { useToastStore } from '../store/toast';

function getErrorMessage(error: unknown, fallback: string) {
  const candidate = error as { response?: { data?: { message?: string; error?: { message?: string } } }; message?: string };
  return candidate?.response?.data?.message || candidate?.response?.data?.error?.message || candidate?.message || fallback;
}

export function AdminOperatorsPage() {
  const [operators, setOperators] = useState<Array<Record<string, string>>>([]);
  const [selectedOperatorId, setSelectedOperatorId] = useState('');
  const [submitting, setSubmitting] = useState<'create' | 'update' | 'delete' | null>(null);
  const pushToast = useToastStore((s) => s.pushToast);

  const refresh = async () => {
    try {
      const data = await fetchOperators();
      setOperators(data ?? []);
      if (!selectedOperatorId && (data ?? []).length > 0) {
        setSelectedOperatorId(String((data ?? [])[0].operator_id ?? ''));
      }
    } catch (error) {
      pushToast(getErrorMessage(error, 'Failed to load operators.'), 'error');
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const onCreate = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const operatorId = String(fd.get('operator_id') ?? '').trim();
    const name = String(fd.get('name') ?? '').trim();
    const password = String(fd.get('password') ?? '').trim();
    if (!operatorId || !name || password.length < 8) {
      pushToast('Operator ID, name and password (min 8 chars) are required.', 'error');
      return;
    }

    setSubmitting('create');
    try {
      await createOperator({
        operator_id: operatorId,
        name,
        email: String(fd.get('email') ?? '').trim() || undefined,
        password,
        status: String(fd.get('status') ?? 'active') === 'inactive' ? 'inactive' : 'active',
      });
      pushToast(`Operator ${operatorId} created.`, 'success');
      e.currentTarget.reset();
      await refresh();
      setSelectedOperatorId(operatorId);
    } catch (error) {
      pushToast(getErrorMessage(error, 'Create operator failed.'), 'error');
    } finally {
      setSubmitting(null);
    }
  };

  const onUpdate = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const operatorId = String(fd.get('target_operator_id') ?? '').trim();
    if (!operatorId) {
      pushToast('Select an operator to update.', 'error');
      return;
    }

    const payload: { name?: string; email?: string; status?: 'active' | 'inactive' } = {};
    const name = String(fd.get('name') ?? '').trim();
    const email = String(fd.get('email') ?? '').trim();
    const status = String(fd.get('status') ?? '').trim();
    if (name) payload.name = name;
    if (email) payload.email = email;
    if (status === 'active' || status === 'inactive') payload.status = status;

    if (Object.keys(payload).length === 0) {
      pushToast('Provide at least one field to update.', 'info');
      return;
    }

    setSubmitting('update');
    try {
      await updateOperator(operatorId, payload);
      pushToast(`Operator ${operatorId} updated.`, 'success');
      await refresh();
    } catch (error) {
      pushToast(getErrorMessage(error, 'Update operator failed.'), 'error');
    } finally {
      setSubmitting(null);
    }
  };

  const onDelete = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const operatorId = String(fd.get('delete_operator_id') ?? '').trim();
    if (!operatorId) {
      pushToast('Select an operator to delete.', 'error');
      return;
    }

    setSubmitting('delete');
    try {
      await deleteOperator(operatorId);
      pushToast(`Operator ${operatorId} deleted.`, 'success');
      await refresh();
      if (selectedOperatorId === operatorId) {
        setSelectedOperatorId('');
      }
    } catch (error) {
      pushToast(getErrorMessage(error, 'Delete operator failed.'), 'error');
    } finally {
      setSubmitting(null);
    }
  };

  return (
    <section className='stack-lg'>
      <article className='card'>
        <h2>Create Operator</h2>
        <form autoComplete='off' className='stack form-grid' onSubmit={onCreate}>
          <input aria-hidden='true' autoComplete='username' style={{ display: 'none' }} tabIndex={-1} />
          <input aria-hidden='true' autoComplete='new-password' style={{ display: 'none' }} tabIndex={-1} type='password' />
          <input autoComplete='off' name='operator_id' placeholder='Operator ID (example: op_101)' required />
          <input autoComplete='off' name='name' placeholder='Operator Name' required />
          <input autoComplete='off' name='email' placeholder='operator@org.com' />
          <input autoComplete='new-password' name='password' type='password' placeholder='Set Password' required />
          <select name='status' defaultValue='active'>
            <option value='active'>active</option>
            <option value='inactive'>inactive</option>
          </select>
          <button className='primary-btn' disabled={submitting === 'create'} type='submit'>
            {submitting === 'create' ? 'Creating...' : 'Create Operator'}
          </button>
        </form>
      </article>

      <article className='card'>
        <h2>Update / Delete Operator</h2>
        <form autoComplete='off' className='stack form-grid' onSubmit={onUpdate}>
          <select name='target_operator_id' value={selectedOperatorId} onChange={(e) => setSelectedOperatorId(e.target.value)}>
            <option value=''>Select operator</option>
            {operators.map((op) => (
              <option key={op.operator_id} value={op.operator_id}>
                {op.operator_id}
              </option>
            ))}
          </select>
          <input autoComplete='off' name='name' placeholder='New name (optional)' />
          <input autoComplete='off' name='email' placeholder='New email (optional)' />
          <select name='status' defaultValue=''>
            <option value=''>status unchanged</option>
            <option value='active'>active</option>
            <option value='inactive'>inactive</option>
          </select>
          <button className='ghost-btn' disabled={submitting === 'update'} type='submit'>
            {submitting === 'update' ? 'Updating...' : 'Update Operator'}
          </button>
        </form>

        <form autoComplete='off' className='stack form-grid' onSubmit={onDelete}>
          <select name='delete_operator_id' defaultValue=''>
            <option value=''>Select operator</option>
            {operators.map((op) => (
              <option key={op.operator_id} value={op.operator_id}>
                {op.operator_id}
              </option>
            ))}
          </select>
          <button className='ghost-btn' disabled={submitting === 'delete'} type='submit'>
            {submitting === 'delete' ? 'Deleting...' : 'Delete Operator'}
          </button>
        </form>
      </article>

      <article className='card'>
        <h2>Operators</h2>
        <div className='table-wrap'>
          <table>
            <thead>
              <tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr>
            </thead>
            <tbody>
              {operators.map((op) => (
                <tr key={op.operator_id}>
                  <td>{op.operator_id}</td>
                  <td>{op.name}</td>
                  <td>{op.email}</td>
                  <td>{op.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
