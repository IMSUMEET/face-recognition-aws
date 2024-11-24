# Grading Script

# -------------------------- PART 1 --------------------------
# there was no --output_bucket I added it
# python grading_scripts/grader_script_p1.py --access_key <process.env.GRADER_ACCESS_KEY> --secret_key <process.env.GRADER_SECRET_KEY> --input_bucket <process.env.ASU_ID>-input --output_bucket <process.env.ASU_ID>-stage-1 --lambda_name video-splitting

# Workload Generator
# There was error if i provided just --asu_id hence added 2 fields --input_bucket --output_bucket
# Test-Case-1
# python3 workload_generator/workload_generator.py --access_key <process.env.GRADER_ACCESS_KEY> --secret_key <process.env.GRADER_SECRET_KEY> --input_bucket <process.env.ASU_ID>-input --testcase_folder dataset/test_case_1/ --output_bucket <process.env.ASU_ID>-stage-1


# Test-Case-2
# python3 workload_generator/workload_generator.py --access_key <process.env.GRADER_ACCESS_KEY> --secret_key <process.env.GRADER_SECRET_KEY> --input_bucket <process.env.ASU_ID>-input --testcase_folder dataset/test_case_2/ --output_bucket <process.env.ASU_ID>-stage-1

# -------------------------- PART 2 --------------------------

# python grading_scripts/grader_script_p2_v2.py --access_key <process.env.GRADER_ACCESS_KEY> --secret_key <process.env.GRADER_SECRET_KEY> --asu_id <process.env.ASU_ID>

# Workload Generator
# There was error if i provided just --asu_id hence added 2 fields --input_bucket --output_bucket
# Test-Case-1
# python3 workload_generator/workload_generator.py --access_key <process.env.GRADER_ACCESS_KEY> --secret_key <process.env.GRADER_SECRET_KEY> --input_bucket <process.env.ASU_ID>-input --testcase_folder dataset/test_case_1/ --output_bucket <process.env.ASU_ID>-stage-1

# Test-Case-2
# python3 workload_generator/workload_generator.py --access_key <process.env.GRADER_ACCESS_KEY> --secret_key <process.env.GRADER_SECRET_KEY> --input_bucket <process.env.ASU_ID>-input --testcase_folder dataset/test_case_2/ --output_bucket <process.env.ASU_ID>-stage-1