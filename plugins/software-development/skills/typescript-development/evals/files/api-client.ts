type User = { profile: { name: string } };

export async function loadName(response: Response): Promise<string> {
  const user = (await response.json()) as User;
  return user.profile.name;
}
