#!/bin/bash
# Start test database container

set -e

echo "Starting test database..."
docker-compose -f docker-compose.test.yml up -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
until docker-compose -f docker-compose.test.yml exec -T test-db pg_isready -U test -d baby_diary_test; do
  sleep 1
done

echo "Test database is ready!"
echo "Connection: postgresql://test:test@localhost:5433/baby_diary_test"