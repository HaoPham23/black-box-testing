from BaseTestSuite import BaseTestSuite
import json


class TestRunner():
    @staticmethod
    def test(test_suite: BaseTestSuite, test_name: str):
        #### Find test func, it starts with "test..."
        test_func = None
        all_attributes = dir(test_suite)
        # Filter and run methods starting with "test"
        for attr in all_attributes:
            if attr.startswith("test") and callable(getattr(test_suite, attr)):
                # Call the method
                test_func = getattr(test_suite, attr)
                break
        
        #### Save result
        test_dict = test_suite.data
        result = []
        for test in test_dict.values():
            result.append(test_func(test))
        fail_test_name = []
        for i in range(0, len(result)):
            if not result[i]:
                fail_test_name.append(list(test_dict.keys())[i])

        fail_test_name_str = 'FAILED:\n\t'+ '\n\t'.join(name for name in fail_test_name) if len(fail_test_name) != 0 else 'Fail testcase: None'
        print(f"""
        \n- Test {test_name} (Level 1) --\nPASSED: {result.count(True)}/{len(result)}\n{fail_test_name_str}\n
        """)
        
    @staticmethod
    def run(test_suite, test_name: str):
        test_suite.setup_method(None)
        result = TestRunner.test(test_suite, test_name)
        test_suite.teardown_method(None)
        return result