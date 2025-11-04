import bcrypt

# 生成 password 的 hash
password = b'password'
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
hashed_str = hashed.decode('utf-8')

print(f'Password: {password.decode()}')
print(f'Hash: {hashed_str}')
print(f'Hash Length: {len(hashed_str)}')
print(f'Verification: {bcrypt.checkpw(password, hashed)}')
