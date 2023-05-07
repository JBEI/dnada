export const getLocalToken = () => localStorage.getItem('token');

export const saveLocalToken = (token: string) =>
  localStorage.setItem('token', token);

export const removeLocalToken = () => localStorage.removeItem('token');

export function forceFileDownload(data: any, fileName: string) {
  const url = window.URL.createObjectURL(new Blob([data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', fileName);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function basename(str: string, sep: string): string {
  return str.substr(str.lastIndexOf(sep) + 1);
}

export function stripExtension(str: string): string {
  return str.substr(0, str.lastIndexOf('.'));
}
