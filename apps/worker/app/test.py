from app.tasks import task_test_generation

# Bắn thẳng task vào queue agent.test_generation
result = task_test_generation.apply_async(kwargs={"payload": {"application_id": "9e0f4edd-8d0e-4fd2-a1bb-eb40d4845424"}})

print(f"Task ID: {result.id}")