from promise import Promise
from promise.dataloader import DataLoader as BaseDataloader


class DataLoader(BaseDataloader):

    def __init__(self):
        super().__init__()

    def batch_load_fn(self, keys):
        results = self.batch_load(keys)
        return Promise.resolve(results)
